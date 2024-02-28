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
    assert agent._upstream is not None
    assert agent._downstream is not None
    assert agent._file_paths == []
    assert agent._prompt == ""
    assert agent.explanations == []
    assert agent.responses == []
    assert agent.commit_msg == ""
    assert agent._cache is not None

@patch("agent.encode_to_base64")
@patch("agent.decode_from_base64")
@patch("agent.get_completion")
@patch("agent.json.loads")
@patch("agent.Cache")
def test_solve_merge_conflict_cache_miss(mock_cache_class, mock_json_loads, mock_get_completion, mock_decode, mock_encode):
    # Arrange
    mock_cache = MagicMock()
    mock_cache_class.return_value = mock_cache
    mock_cache.lookup.return_value = False
    mock_encode.side_effect = ["encoded_prompt", "encoded_response"]
    mock_get_completion.return_value = '{"explanation": "explanation", "code": "code"}'
    mock_json_loads.return_value = {"explanation": "explanation", "code": "code"}
    mock_decode.return_value = '{"explanation": "explanation", "code": "code"}'
    agent = Agent("downstream", "upstream")
    agent._prompt = "prompt"

    # Act
    response = agent.solve_merge_conflict()

    # Assert
    mock_encode.assert_any_call("prompt")
    mock_encode.assert_any_call({"explanation": "explanation", "code": "code"})
    mock_cache.lookup.assert_called_once_with("encoded_prompt")
    mock_get_completion.assert_called_once_with("prompt", type="json_object")
    mock_cache.update.assert_called_once_with("encoded_prompt", "encoded_response")
    mock_json_loads.assert_called_once_with('{"explanation": "explanation", "code": "code"}')
    assert agent.explanations == ["explanation"]
    assert agent.responses == ["code"]
    assert response == {"explanation": "explanation", "code": "code"}

@patch("agent.encode_to_base64")
@patch("agent.decode_from_base64")
@patch("agent.get_completion")
@patch("agent.json.loads")
@patch("agent.Cache")
def test_solve_merge_conflict_cache_hit(mock_cache_class, mock_json_loads, mock_get_completion, mock_decode, mock_encode):
    # Arrange
    mock_cache = MagicMock()
    mock_cache_class.return_value = mock_cache
    mock_cache.lookup.return_value = "encoded_response"
    mock_cache.get_answer.return_value = "encoded_response"
    mock_encode.return_value = "encoded_prompt"
    mock_decode.return_value = '{"explanation": "explanation", "code": "code"}'
    agent = Agent("downstream", "upstream")
    agent._prompt = "prompt"

    # Act
    response = agent.solve_merge_conflict()

    # Assert
    mock_encode.assert_called_once_with("prompt")
    mock_cache.lookup.assert_called_once_with("encoded_prompt")
    mock_decode.assert_called_once_with("encoded_response")
    assert response == {"explanation": "explanation", "code": "code"}

@patch("agent.get_completion")
def test_make_commit_msg(mock_get_completion, agent):
    mock_get_completion.return_value = "mock_commit_msg"
    agent.explanations = ["explanation1", "explanation2"]
    agent.make_commit_msg()
    assert agent.commit_msg == "mock_commit_msg"

def test_make_prompt(agent):
    file_path = "mock_file_path"
    file_content = "mock_file_content"
    expected_prompt = merge_prompt.format(file_content=file_content)
    result_prompt = agent.make_prompt(file_path, file_content)
    assert agent._file_paths == [file_path]
    assert agent._prompt == expected_prompt
    assert result_prompt == expected_prompt

def test_write_responses(agent):
    agent._file_paths = ["mock_file_path1", "mock_file_path2"]
    agent.responses = ["mock_response1", "mock_response2"]
    m = mock_open()
    with patch("builtins.open", m), \
         patch("os.path.join", return_value="mock_full_path") as mock_join, \
         patch("agent.downstream_path", new="mock_downstream_path"):
        agent.write_responses()
    mock_join.assert_any_call("mock_downstream_path", "mock_file_path1")
    mock_join.assert_any_call("mock_downstream_path", "mock_file_path2")
    m.assert_any_call("mock_full_path", "w")
    m().write.assert_any_call("mock_response1")
    m().write.assert_any_call("mock_response2")

def test_git_actions(agent):
    # Mock the _downstream.git object
    agent._downstream.git = MagicMock()

    # Set up the test data
    agent._file_paths = ["file1.py", "file2.py"]
    agent.commit_msg = "Test commit"
    agent._downstream.active_branch.name = "main"

    # Call the method to test
    agent.git_actions()

    # Assert that the add, commit, and push methods were called with the correct arguments
    agent._downstream.git.add.assert_called_once_with(agent._file_paths)
    agent._downstream.git.commit.assert_called_once_with("-m", agent.commit_msg)
    agent._downstream.git.push.assert_called_once_with("--set-upstream",
                                                       "origin",
                                                       agent._downstream.active_branch.name)

@patch("agent.Auth.Token")
@patch("agent.Github")
def test_create_pull_request(mock_github, mock_auth_token, agent):
    # Set up the mock objects
    mock_auth_token.return_value = "mock_token"
    mock_github.return_value.get_user.return_value.login = "mock_login"
    mock_repo = MagicMock()
    mock_github.return_value.get_repo.return_value = mock_repo

    # Set up the test data
    agent._file_paths = ["file1.py", "file2.py"]
    agent.explanations = ["Explanation 1", "Explanation 2"]
    agent._downstream.active_branch.name = "main"

    # Call the method to test
    agent.create_pull_request()

    # Assert that the Github and Repo methods were called with the correct arguments
    mock_auth_token.assert_called_once_with("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")
    mock_github.assert_called_once_with(auth="mock_token")
    mock_github.return_value.get_repo.assert_called_once_with("Ki-Reply-GmbH/uc-postal-tracking_routeCalc")
    mock_repo.create_pull.assert_called_once_with(
        title="Automated AI merge conflict resolution",
        body="**Our AI has resolved the merge conflicts in the following files:**\n\n**file1.py**:\nExplanation 1\n\n**file2.py**:\nExplanation 2\n\n",
        head="main",
        base="main"
    )