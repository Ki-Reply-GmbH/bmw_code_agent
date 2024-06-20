import pytest
import os
import pandas as pd
from cache import Cache


@pytest.fixture
def cache():
    c = Cache(cache_folder='.unit_test_cache', cache_file=
        'unit_test_prompts.csv')
    yield c
    for filename in os.listdir(c.cache_folder):
        file_path = os.path.join(c.cache_folder, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
    if os.path.exists(c.cache_folder):
        os.rmdir(c.cache_folder)


def test_init(cache):
    """
    Test the initialization of the Cache object by verifying the existence of the cache folder and cache file.
    It also checks if the cache file is initially empty, ensuring that the setup is correct for further operations.
    """
    assert os.path.exists(cache.cache_folder)
    assert os.path.exists(cache.cache_file)
    df = pd.read_csv(cache.cache_file)
    assert df.empty


def test_update(cache):
    """
    Tests the update method of the Cache class to ensure it correctly updates the cache with a new prompt and answer pair.

    This test performs the following:
    - Updates the cache with a specified prompt and answer.
    - Verifies that the return value of the update method is 0, indicating success.
    - Checks that the prompt is correctly added to the main cache file.
    - Ensures that the answer is stored in a separate file corresponding to the prompt's index and that the content matches the expected answer.
    """
    prompt = 'test_prompt'
    answer = 'test_answer'
    assert cache.update(prompt, answer) == 0
    df = pd.read_csv(cache.cache_file)
    assert prompt in df['prompt'].values
    answer_df = pd.read_csv(f'{cache.cache_folder}/0.csv')
    assert answer_df['answer'].values[0] == answer


def test_delete(cache):
    """
    Tests the deletion of a prompt and its associated answer from the cache.

    This test performs the following:
    1. Adds a prompt and its answer to the cache.
    2. Deletes the prompt from the cache.
    3. Verifies that the prompt is no longer present in the cache.
    4. Ensures that the file associated with the deleted prompt is also removed.
    """
    prompt = 'test_prompt'
    answer = 'test_answer'
    cache.update(prompt, answer)
    cache.delete(prompt)
    df = pd.read_csv(cache.cache_file)
    assert prompt not in df['prompt'].values
    assert not os.path.exists(f'{cache.cache_folder}/0.csv')


def test_lookup(cache):
    """
    Tests the lookup functionality of the Cache class to ensure it correctly identifies whether a prompt exists in the cache.

    This test involves:
    1. Verifying that a prompt not present in the cache returns False.
    2. Adding a prompt to the cache and then verifying that the lookup returns True.
    """
    prompt = 'test_prompt'
    answer = 'test_answer'
    assert not cache.lookup(prompt)
    cache.update(prompt, answer)
    assert cache.lookup(prompt)


def test_get_answer(cache):
    """
    Tests the `get_answer` method of the Cache class to ensure it correctly retrieves the answer for a given prompt.

    This test checks two scenarios:
    1. When the prompt does not exist in the cache, ensuring that the method returns None.
    2. After updating the cache with a prompt-answer pair, verifying that the method returns the correct answer for the prompt.
    """
    prompt = 'test_prompt'
    answer = 'test_answer'
    assert cache.get_answer(prompt) is None
    cache.update(prompt, answer)
    assert cache.get_answer(prompt) == answer
