import pytest
import os
import pandas as pd
from cache import Cache

@pytest.fixture
def cache():
    c = Cache(cache_folder=".unit_test_cache", cache_file="unit_test_prompts.csv")
    yield c
    # Clean up function
    for filename in os.listdir(c.cache_folder):
        file_path = os.path.join(c.cache_folder, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
    if os.path.exists(c.cache_folder):
        os.rmdir(c.cache_folder)

def test_init(cache):
    assert os.path.exists(cache.cache_folder)
    assert os.path.exists(cache.cache_file)
    df = pd.read_csv(cache.cache_file)
    assert df.empty

def test_update(cache):
    prompt = "test_prompt"
    answer = "test_answer"
    assert cache.update(prompt, answer) == 0
    df = pd.read_csv(cache.cache_file)
    assert prompt in df["prompt"].values
    answer_df = pd.read_csv(f"{cache.cache_folder}/0.csv")
    assert answer_df["answer"].values[0] == answer

def test_delete(cache):
    prompt = "test_prompt"
    answer = "test_answer"
    cache.update(prompt, answer)
    cache.delete(prompt)
    df = pd.read_csv(cache.cache_file)
    assert prompt not in df["prompt"].values
    assert not os.path.exists(f"{cache.cache_folder}/0.csv")

def test_lookup(cache):
    prompt = "test_prompt"
    answer = "test_answer"
    assert not cache.lookup(prompt)
    cache.update(prompt, answer)
    assert cache.lookup(prompt)

def test_get_answer(cache):
    prompt = "test_prompt"
    answer = "test_answer"
    assert cache.get_answer(prompt) is None
    cache.update(prompt, answer)
    assert cache.get_answer(prompt) == answer