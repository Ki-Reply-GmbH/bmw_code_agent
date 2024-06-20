import pytest
import os
from agent import Agent
from cache import Cache
from functions import encode_to_base64
from .test_prompts import test_prompt1, test_prompt2, test_prompt3, test_result1, test_result2, test_result3
current_dir_path = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def agent():
    """
    Creates and returns an Agent instance initialized with specified downstream and upstream URLs.

    The `agent` fixture is used for setting up an Agent object with predefined downstream and upstream repository URLs. This setup is typically used in tests to simulate the behavior of an agent handling interactions between these repositories.

    Returns:
        Agent: An instance of the Agent class initialized with the provided URLs.
    """
    downstream = (
        'https://github.com/Ki-Reply-GmbH/uc-postal-tracking_routeCalc.git')
    upstream = 'https://github.com/Ki-Reply-GmbH/uc-postal-tracking.git'
    return Agent(downstream, upstream)


@pytest.mark.parametrize('prompt,expected_response', [(test_prompt1,
    test_result1), (test_prompt2, test_result2), (test_prompt3, test_result3)])
def test_solve_merge_conflict_cache_hit(agent, prompt, expected_response):
    """
    Test the `solve_merge_conflict` method of the `Agent` class when there is a cache hit.

    This test checks if the `solve_merge_conflict` method correctly retrieves the expected response from the cache when the prompt has been cached previously. It ensures that the method:
    1. Sets the `_prompt` attribute of the agent to the given prompt.
    2. Initializes the `_cache` with a specific cache folder and file.
    3. Correctly retrieves the response from the cache without recalculating it.
    4. Asserts that the cached response matches the expected response.

    Parameters:
        agent (Agent): The agent instance configured with necessary upstream and downstream URLs.
        prompt (str): The input prompt for which the merge conflict solution is to be retrieved.
        expected_response (str): The expected response from the cache for the given prompt.

    Uses fixtures:
        agent: Provides an initialized instance of `Agent` with predefined URLs.
    """
    agent._prompt = prompt
    agent._cache = Cache(cache_folder=os.path.join(current_dir_path,
        '.module_test_cache'), cache_file='module_test_prompts.csv')
    response = agent.solve_merge_conflict()
    assert agent._prompt == prompt
    assert agent._cache.lookup(encode_to_base64(prompt)) == True
    assert response == expected_response
