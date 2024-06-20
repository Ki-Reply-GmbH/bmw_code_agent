import os
import tempfile
from unittest.mock import MagicMock, Mock, patch
from git_handler import GitHandler


@patch('git_handler.Repo')
def test_initialize_repo(mock_repo):
    """
    Tests the initialization of the GitHandler repository by cloning from specified URLs and setting up remotes.

    This test function uses the `mock_repo` object to simulate the cloning of repositories from provided URLs. It verifies:
    - The `Repo.clone_from` method is called twice to clone both the route calculation and tracking repositories.
    - A remote named 'upstream' is created for the downstream repository.
    - The newly created remote is fetched.
    - A feature branch is created in the downstream repository.
    - The feature branch is checked out.

    The function asserts these operations to ensure the GitHandler's initialization process is functioning as expected.
    """
    mock_repo.clone_from.return_value = MagicMock()
    gh = GitHandler(
        'https://github.com/Ki-Reply-GmbH/uc-postal-tracking_routeCalc.git',
        'https://github.com/Ki-Reply-GmbH/uc-postal-tracking.git')
    assert mock_repo.clone_from.call_count == 2
    gh._downstream.create_remote.assert_called_once_with('upstream', url=
        'https://github.com/Ki-Reply-GmbH/uc-postal-tracking.git')
    gh._downstream.create_remote.return_value.fetch.assert_called_once()
    gh._downstream.create_head.assert_called_once()
    gh._downstream.git.checkout.assert_called_once_with(gh._feature_branch)


def test_analyse_files():
    """
    Tests the analysis of files in a Git repository by simulating the identification of unmerged blobs.

    This test function mocks the GitHandler's internal methods to avoid actual Git operations. It sets up a scenario where the GitHandler instance is expected to identify unmerged file paths from a repository's index. The test verifies that the GitHandler correctly populates its internal list of unmerged file paths based on the mocked data.
    """
    downstream_mock = Mock()
    downstream_mock.index.unmerged_blobs.return_value = ['path1', 'path2',
        'path3']
    with patch.object(GitHandler, '_initialize_repo', return_value=None
        ), patch.object(GitHandler, '_run_workflow', return_value=None):
        handler = GitHandler('downstream_url', 'upstream_url')
        handler._downstream = downstream_mock
        handler._analyse_files()
        assert handler._unmerged_filepaths == ['path1', 'path2', 'path3']


@patch('git_handler.Repo')
def test_try_to_merge(mock_repo):
    """
    Tests the `_try_to_merge` method of the `GitHandler` class to ensure it attempts to merge branches and returns a boolean indicating the success of the merge operation.
    """
    mock_repo.clone_from.return_value = MagicMock()
    gh = GitHandler(
        'https://github.com/Ki-Reply-GmbH/uc-postal-tracking_routeCalc.git',
        'https://github.com/Ki-Reply-GmbH/uc-postal-tracking.git')
    result = gh._try_to_merge()
    assert isinstance(result, bool)


def test_clean_up():
    """
    Tests the clean-up process by creating a temporary directory structure, invoking the clean-up method, and verifying the removal of the directory.

    This test function simulates the clean-up process in the GitHandler class by:
    1. Creating a temporary directory and a nested structure within it.
    2. Writing a test file in the nested directory.
    3. Patching the GitHandler's initialization and workflow methods to prevent actual Git operations.
    4. Patching the os.path.dirname to return the temporary directory path.
    5. Initializing a GitHandler instance and invoking the _clean_up method.
    6. Asserting that the temporary directory is successfully removed after the clean-up operation.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        os.makedirs(os.path.join(tmp_dir, '.tmp', 'subdir'))
        with open(os.path.join(tmp_dir, '.tmp', 'file.txt'), 'w') as f:
            f.write('test')
        with patch('git_handler.GitHandler._initialize_repo', return_value=None
            ), patch('git_handler.GitHandler._run_workflow', return_value=None
            ), patch('git_handler.os.path.dirname', return_value=tmp_dir):
            handler = GitHandler('downstream_url', 'upstream_url')
            handler._clean_up()
        assert not os.path.exists(os.path.join(tmp_dir, '.tmp'))


def test_get_unmerged_filepaths():
    """
    Tests the `get_unmerged_filepaths` method of the `GitHandler` class to ensure it returns the correct list of unmerged file paths.

    This test initializes a `GitHandler` instance, sets a predefined list of unmerged file paths, and then retrieves this list using the `get_unmerged_filepaths` method. It asserts that the returned list matches the expected list of file paths.
    """
    with patch.object(GitHandler, '_initialize_repo', return_value=None
        ), patch.object(GitHandler, '_run_workflow', return_value=None):
        handler = GitHandler('downstream_url', 'upstream_url')
        handler._unmerged_filepaths = ['path1', 'path2', 'path3']
        result = handler.get_unmerged_filepaths()
        assert result == ['path1', 'path2', 'path3']


def test_get_f_content():
    """
    Fetches the content of a file based on its index from the list of unmerged file contents.

    Args:
        index (int): The index of the file content to retrieve from the list.

    Returns:
        str: The content of the file at the specified index.

    Raises:
        IndexError: If the index is out of the range of the list.
    """
    with patch('git_handler.GitHandler._initialize_repo', return_value=None
        ), patch('git_handler.GitHandler._run_workflow', return_value=None):
        handler = GitHandler('downstream_url', 'upstream_url')
        handler._unmerged_filecontents = ['content1', 'content2', 'content3']
        result = handler.get_f_content(1)
        assert result == 'content2'
