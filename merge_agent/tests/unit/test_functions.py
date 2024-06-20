import pytest
import os
import base64
from functions import encode_to_base64, decode_from_base64


@pytest.fixture
def test_cases():
    cases = ['Hello, World!', 'Whole conflict',
        "{'Special Characters': '+*/--?`=#äüö'}", '']
    return cases


def test_encode_to_base64(test_cases):
    """
    Test the `encode_to_base64` function by ensuring it correctly encodes a list of test strings into Base64 format.

    This test iterates over a list of strings provided by the `test_cases` fixture and checks if the output from `encode_to_base64` matches the expected Base64 encoded result of each string.

    Parameters:
        test_cases (list of str): A list of strings to be encoded into Base64.

    Raises:
        AssertionError: If the encoded result does not match the expected Base64 encoded string.
    """
    for test_string in test_cases:
        assert encode_to_base64(test_string) == base64.b64encode(test_string
            .encode()).decode()


def test_decode_from_base64(test_cases):
    """
    Test the `decode_from_base64` function to ensure it correctly decodes a base64 encoded string back to its original form.

    This test iterates over a list of test cases, encodes each string into base64, and then uses the `decode_from_base64` function to decode it, checking if the decoded string matches the original string.

    Parameters:
        test_cases (list): A list of strings to be tested for correct base64 decoding.

    Raises:
        AssertionError: If the decoded string does not match the original string.
    """
    for test_string in test_cases:
        encoded_string = base64.b64encode(test_string.encode()).decode()
        assert decode_from_base64(encoded_string) == test_string


def test_format_file():
    """
    Test the `format_file` function to ensure it correctly formats files as expected.

    This function is currently a placeholder and needs to be implemented. Once implemented,
    it should be tested to verify that it formats files according to specified requirements.
    """
    pass
