import os
import tempfile
from unittest.mock import MagicMock, Mock, patch
from git_handler import GitHandler

@patch("git_handler.Repo")
def test_initialize_repo(mock_repo):
    mock_repo.clone_from.return_value = MagicMock()
    gh = GitHandler("https://github.com/Ki-Reply-GmbH/uc-postal-tracking_routeCalc.git",
                    "https://github.com/Ki-Reply-GmbH/uc-postal-tracking.git")
    
    # Assert that Repo.clone_from was called twice
    assert mock_repo.clone_from.call_count == 2

    # Assert that a remote was created
    gh._downstream.create_remote.assert_called_once_with("upstream", url="https://github.com/Ki-Reply-GmbH/uc-postal-tracking.git")

    # Assert that the remote was fetched
    gh._downstream.create_remote.return_value.fetch.assert_called_once()

    # Assert that a feature branch was created
    gh._downstream.create_head.assert_called_once()

    # Assert that the feature branch was checked out
    gh._downstream.git.checkout.assert_called_once_with(gh._feature_branch)

def test_analyse_files():
    # Create a mock for the _downstream attribute
    downstream_mock = Mock()
    # Set the return value for the unmerged_blobs method
    downstream_mock.index.unmerged_blobs.return_value = ["path1", "path2", "path3"]

    # Create a GitHandler instance with the mock
    with patch.object(GitHandler, "_initialize_repo", return_value=None), \
         patch.object(GitHandler, "_run_workflow", return_value=None):
        # Mock the _initialize_repo method, so that no real GitHubs repos are cloned.
        handler = GitHandler("downstream_url", "upstream_url")
        handler._downstream = downstream_mock

        # Call the _analyse_files method
        handler._analyse_files()

        # Check if the _unmerged_filepaths attribute was correctly populated
        assert handler._unmerged_filepaths == ["path1", "path2", "path3"]

@patch("git_handler.Repo")
def test_try_to_merge(mock_repo):
    mock_repo.clone_from.return_value = MagicMock()
    gh = GitHandler("https://github.com/Ki-Reply-GmbH/uc-postal-tracking_routeCalc.git",
                    "https://github.com/Ki-Reply-GmbH/uc-postal-tracking.git")
    result = gh._try_to_merge()
    assert isinstance(result, bool)

def test_clean_up():
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a subdirectory and a file in the temporary directory
        os.makedirs(os.path.join(tmp_dir, ".tmp", "subdir"))
        with open(os.path.join(tmp_dir, ".tmp", "file.txt"), "w") as f:
            f.write("test")

        # Create a GitHandler instance with the mock
        with patch("git_handler.GitHandler._initialize_repo", return_value=None), \
             patch("git_handler.GitHandler._run_workflow", return_value=None), \
             patch("git_handler.os.path.dirname", return_value=tmp_dir):
            handler = GitHandler("downstream_url", "upstream_url")

            # Call the _clean_up method
            handler._clean_up()

        # Check if the .tmp directory has been removed
        assert not os.path.exists(os.path.join(tmp_dir, ".tmp"))

def test_get_unmerged_filepaths():
    # Create a GitHandler instance with the mock
    with patch.object(GitHandler, "_initialize_repo", return_value=None), \
         patch.object(GitHandler, "_run_workflow", return_value=None):
        handler = GitHandler("downstream_url", "upstream_url")

        # Set the _unmerged_filepaths attribute
        handler._unmerged_filepaths = ["path1", "path2", "path3"]

        # Call the get_unmerged_filepaths method
        result = handler.get_unmerged_filepaths()

        # Check if the result is correct
        assert result == ["path1", "path2", "path3"]

def test_get_f_content():
    # Create a GitHandler instance with the mock
    with patch("git_handler.GitHandler._initialize_repo", return_value=None), \
         patch("git_handler.GitHandler._run_workflow", return_value=None):
        handler = GitHandler("downstream_url", "upstream_url")

        # Set the _unmerged_filecontents attribute
        handler._unmerged_filecontents = ["content1", "content2", "content3"]

        # Call the get_f_content method
        result = handler.get_f_content(1)

        # Check if the result is correct
        assert result == "content2"