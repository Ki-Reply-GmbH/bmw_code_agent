import pytest
import os
import base64
from functions import encode_to_base64, decode_from_base64

@pytest.fixture
def test_cases():
    cases = [
        "Hello, World!",
        "Whole conflict",
        "{'Special Characters': '+*/--?`=#äüö'}",
        "",
        ]
    return cases

def test_encode_to_base64(test_cases):
    for test_string in test_cases:
        assert encode_to_base64(test_string) == base64.b64encode(test_string.encode()).decode()

def test_decode_from_base64(test_cases):
    for test_string in test_cases:
        encoded_string = base64.b64encode(test_string.encode()).decode()
        assert decode_from_base64(encoded_string) == test_string

#TODO Test the format_file function as soon as it is implemented
def test_format_file():
    pass