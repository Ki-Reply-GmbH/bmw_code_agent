import pytest
import base64
from unittest.mock import mock_open, patch, MagicMock
from agent import Agent
from prompts import merge_prompt


@pytest.fixture
def agent():
    downstream = MagicMock()
    upstream = MagicMock()
    return Agent(downstream, upstream)


def test_init(agent):
    """
    Test the initialization of an Agent instance to ensure all properties are set correctly.

    This test checks that the Agent's upstream and downstream attributes are not None,
    the file paths list is empty, the prompt string is empty, the explanations list is empty,
    the responses list is empty, the commit message is empty, and the cache is not None.
    """
    assert agent._upstream is not None
    assert agent._downstream is not None
    assert agent._file_paths == []
    assert agent._prompt == ''
    assert agent.explanations == []
    assert agent.responses == []
    assert agent.commit_msg == ''
    assert agent._cache is not None


@patch('agent.encode_to_base64')
@patch('agent.decode_from_base64')
@patch('agent.get_completion')
@patch('agent.json.loads')
@patch('agent.Cache')
def test_solve_merge_conflict_cache_miss(mock_cache_class, mock_json_loads,
    mock_get_completion, mock_decode, mock_encode):
    """
        ""\"
        Test the behavior of solving a merge conflict when the cache misses.

        This test ensures that when the cache does not have an entry for the given prompt,
        the system correctly encodes the prompt, retrieves a completion from an external
        service, decodes the response, updates the cache with the new response, and
        correctly updates the agent's internal state with the explanations and responses.

        The test uses mocks for the cache system, JSON loading, and the external service
        to simulate the behavior and verify interactions.

        Args:
            mock_cache_class (MagicMock): Mock of the Cache class.
            mock_json_loads (MagicMock): Mock of json.loads function.
            mock_get_completion (MagicMock): Mock of the function to get completion from an external service.
            mock_decode (MagicMock): Mock of the function to decode base64 encoded strings.
            mock_encode (MagicMock): Mock of the function to encode strings to base64.
        ""\"
    """
    mock_cache = MagicMock()
    mock_cache_class.return_value = mock_cache
    mock_cache.lookup.return_value = False
    mock_encode.side_effect = ['encoded_prompt', 'encoded_response']
    mock_get_completion.return_value = (
        '{"explanation": "explanation", "code": "code"}')
    mock_json_loads.return_value = {'explanation': 'explanation', 'code':
        'code'}
    mock_decode.return_value = '{"explanation": "explanation", "code": "code"}'
    agent = Agent('downstream', 'upstream')
    agent._prompt = 'prompt'
    response = agent.solve_merge_conflict()
    mock_encode.assert_any_call('prompt')
    mock_encode.assert_any_call({'explanation': 'explanation', 'code': 'code'})
    mock_cache.lookup.assert_called_once_with('encoded_prompt')
    mock_get_completion.assert_called_once_with('prompt', type='json_object')
    mock_cache.update.assert_called_once_with('encoded_prompt',
        'encoded_response')
    mock_json_loads.assert_called_once_with(
        '{"explanation": "explanation", "code": "code"}')
    assert agent.explanations == ['explanation']
    assert agent.responses == ['code']
    assert response == {'explanation': 'explanation', 'code': 'code'}


@patch('agent.encode_to_base64')
@patch('agent.decode_from_base64')
@patch('agent.get_completion')
@patch('agent.json.loads')
@patch('agent.Cache')
def test_solve_merge_conflict_cache_hit(mock_cache_class, mock_json_loads,
    mock_get_completion, mock_decode, mock_encode):
    """
        ""\"
        Test the `solve_merge_conflict` method of the `Agent` class when a cache hit occurs.

        This test ensures that if the prompt's encoded version is found in the cache, the method retrieves
        the cached response, decodes it, and returns the expected dictionary containing the explanation
        and code without making a call to the external completion API.

        The test uses mocks for:
        - Cache class to simulate cache behavior.
        - JSON loading to simulate decoding of JSON strings.
        - Base64 encoding and decoding to simulate the encoding of prompts and decoding of responses.

        Args:
            mock_cache_class (MagicMock): Mock of the Cache class.
            mock_json_loads (MagicMock): Mock of json.loads function.
            mock_get_completion (MagicMock): Mock of the get_completion method, should not be called.
            mock_decode (MagicMock): Mock of the decode_from_base64 function.
            mock_encode (MagicMock): Mock of the encode_to_base64 function.

        Asserts:
            - The prompt is encoded exactly once.
            - The cache lookup is called with the encoded prompt.
            - The response is decoded from the cached encoded response.
            - The final response matches the expected dictionary output.
        ""\"
    """
    mock_cache = MagicMock()
    mock_cache_class.return_value = mock_cache
    mock_cache.lookup.return_value = 'encoded_response'
    mock_cache.get_answer.return_value = 'encoded_response'
    mock_encode.return_value = 'encoded_prompt'
    mock_decode.return_value = '{"explanation": "explanation", "code": "code"}'
    agent = Agent('downstream', 'upstream')
    agent._prompt = 'prompt'
    response = agent.solve_merge_conflict()
    mock_encode.assert_called_once_with('prompt')
    mock_cache.lookup.assert_called_once_with('encoded_prompt')
    mock_decode.assert_called_once_with('encoded_response')
    assert response == {'explanation': 'explanation', 'code': 'code'}


@patch('agent.get_completion')
def test_make_commit_msg(mock_get_completion, agent):
    """
    Generates a commit message based on the explanations stored in the agent instance.

    This method calls an external service to generate a commit message, which is then stored in the `commit_msg` attribute of the agent. The commit message is generated based on the explanations related to merge conflicts that have been resolved.
    """
    mock_get_completion.return_value = 'mock_commit_msg'
    agent.explanations = ['explanation1', 'explanation2']
    agent.make_commit_msg()
    assert agent.commit_msg == 'mock_commit_msg'


def test_make_prompt(agent):
    """
    Generates a prompt for resolving merge conflicts based on the provided file path and content.

    This method formats a prompt using the file content and updates the agent's internal state
    with the new prompt and the associated file path.

    Args:
        file_path (str): The path to the file involved in the merge conflict.
        file_content (str): The content of the file involved in the merge conflict.

    Returns:
        str: The formatted prompt based on the file content.
    """
    file_path = 'mock_file_path'
    file_content = 'mock_file_content'
    expected_prompt = merge_prompt.format(file_content=file_content)
    result_prompt = agent.make_prompt(file_path, file_content)
    assert agent._file_paths == [file_path]
    assert agent._prompt == expected_prompt
    assert result_prompt == expected_prompt


def test_write_responses(agent):
    """
    Writes the responses generated by the agent to the respective files in the downstream path.

    This method iterates over the file paths and responses stored in the agent, writing each response to its corresponding file. It uses the downstream path to determine the full path for each file. The method ensures that each response is written to the correct file by matching the indices of the file paths and responses lists.
    """
    agent._file_paths = ['mock_file_path1', 'mock_file_path2']
    agent.responses = ['mock_response1', 'mock_response2']
    m = mock_open()
    with patch('builtins.open', m), patch('os.path.join', return_value=
        'mock_full_path') as mock_join, patch('agent.downstream_path', new=
        'mock_downstream_path'):
        agent.write_responses()
    mock_join.assert_any_call('mock_downstream_path', 'mock_file_path1')
    mock_join.assert_any_call('mock_downstream_path', 'mock_file_path2')
    m.assert_any_call('mock_full_path', 'w')
    m().write.assert_any_call('mock_response1')
    m().write.assert_any_call('mock_response2')


def test_git_actions(agent):
    """
    Performs Git actions such as adding, committing, and pushing changes to the repository.

    This method assumes that the agent's `_downstream.git` object is properly configured and that
    the agent has a list of file paths and a commit message prepared. It adds the specified files,
    commits them with the provided commit message, and pushes the changes to the active branch of
    the repository.
    """
    agent._downstream.git = MagicMock()
    agent._file_paths = ['file1.py', 'file2.py']
    agent.commit_msg = 'Test commit'
    agent._downstream.active_branch.name = 'main'
    agent.git_actions()
    agent._downstream.git.add.assert_called_once_with(agent._file_paths)
    agent._downstream.git.commit.assert_called_once_with('-m', agent.commit_msg
        )
    agent._downstream.git.push.assert_called_once_with('--set-upstream',
        'origin', agent._downstream.active_branch.name)


@patch('agent.Auth.Token')
@patch('agent.Github')
def test_create_pull_request(mock_github, mock_auth_token, agent):
    """
    Creates a pull request on GitHub using the resolved merge conflicts and explanations.

    This method authenticates with GitHub, retrieves the user's repository, and creates a pull request
    with a detailed description of the files changed and the explanations for the changes. The pull request
    is made from the active branch to the main branch of the repository.
    """
    mock_auth_token.return_value = 'mock_token'
    mock_github.return_value.get_user.return_value.login = 'mock_login'
    mock_repo = MagicMock()
    mock_github.return_value.get_repo.return_value = mock_repo
    agent._file_paths = ['file1.py', 'file2.py']
    agent.explanations = ['Explanation 1', 'Explanation 2']
    agent._downstream.active_branch.name = 'main'
    agent.create_pull_request()
    mock_auth_token.assert_called_once_with(
        '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')
    mock_github.assert_called_once_with(auth='mock_token')
    mock_github.return_value.get_repo.assert_called_once_with(
        'Ki-Reply-GmbH/uc-postal-tracking_routeCalc')
    mock_repo.create_pull.assert_called_once_with(title=
        'Automated AI merge conflict resolution', body=
        """**Our AI has resolved the merge conflicts in the following files:**

**file1.py**:
Explanation 1

**file2.py**:
Explanation 2

"""
        , head='main', base='main')
