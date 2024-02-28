import pytest
import os
from agent import Agent
from cache import Cache
from functions import encode_to_base64
from .test_prompts import (test_prompt1, test_prompt2,  test_prompt3,
                          test_result1, test_result2, test_result3)

current_dir_path  = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture
def agent():
    downstream = "https://github.com/Ki-Reply-GmbH/uc-postal-tracking_routeCalc.git"
    upstream = "https://github.com/Ki-Reply-GmbH/uc-postal-tracking.git"
    return Agent(downstream, upstream) #downstream and upstream im anderen test case weglassen, damit die Tests in der Pipeline laufen

@pytest.mark.parametrize("prompt,expected_response", [
    (test_prompt1, test_result1),
    (test_prompt2, test_result2),
    (test_prompt3, test_result3)
])
def test_solve_merge_conflict_cache_hit(agent, prompt, expected_response):
    # Arrange
    agent._prompt = prompt
    agent._cache = Cache(cache_folder = os.path.join(current_dir_path, ".module_test_cache"), cache_file = "module_test_prompts.csv")
    
    # Act
    response = agent.solve_merge_conflict()

    # Assert
    assert agent._prompt == prompt
    assert agent._cache.lookup(encode_to_base64(prompt)) == True
    assert response == expected_response