"""
This Python script is designed to resolve merge conflicts in a Git repository 
using an AI model.

The Agent class is initialized with two Git repositories: downstream and upstream.
It has several responsibilities:
1. Analyzing which files have merge conflicts.
2. Solving the merge conflicts using an AI model.
3. Writing the resolved code back to the files.
4. Creating a commit message based on the AI's explanations.
5. Performing Git actions such as add, commit, and push.
6. Creating a pull request in the downstream repository.
"""
import os
import json
import ast
import merge_agent.src.prompts as prompts
import httpx
from openai import AzureOpenAI
from merge_agent.src.functions import encode_to_base64, decode_from_base64
from merge_agent.src.cache import Cache

EXPLANATION, ANSWER = 0, 0
CODE, COMMIT_MSG = 1, 1
git_access_token = os.environ["GIT_ACCESS_TOKEN"]

client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    http_client=httpx.Client(
        proxies=os.environ["HTTPS_PROXY"],
        timeout=httpx.Timeout(60.0, read=60.0)
    )
)

def get_completion(prompt, model=os.environ["JSON-DEPLOYMENT"], type="json_object"): # make global env variable that's used for the model
    """
    Sends a prompt to the OpenAI API and returns the AI"s response.
    """
    messages = [
        {
            "role": "system",
            "content": "You are a system designed to improve code quality."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model"s output,
        response_format={"type": type}
    )
    return response.choices[0].message.content

class MergeAgent():
    """
    The Agent class is designed to solve merge conflicts in a Git repository.
    It has several responsibilities:
    1. Analyzing which files have merge conflicts.
    2. Solving the merge conflicts using an AI model.
    3. Writing the resolved code back to the files.
    4. Creating a commit message based on the AI's explanations.
    5. Performing Git actions such as add, commit, and push.
    6. Creating a pull request in the downstream repository.
    """

    def __init__(self, repo):
        """
        Initializes the Agent with two Git repositories: downstream and upstream.

        Args:
            repo (str): The path to the Git repository.

        The method also initializes several instance variables:
        - _file_paths: A list to store the paths of the files with merge conflicts.
        - _prompt: A string to store the prompt for the AI model.
        - explanations: A list to store the explanations provided by the AI model.
        - responses: A list to store the responses (solutions to the merge conflicts) from the AI model.
        - commit_msg: A string to store the commit message.
        - _cache: An instance of the Cache class to store the responses from the AI model.
        """
        self._repo = repo
        self._file_paths = []
        self._prompt = ""

        self.explanations = []
        self.responses = []
        self.commit_msg = ""

        self._cache = Cache()

    def get_file_paths(self):
        """
        Returns the file paths of the files with merge conflicts.

        Returns:
            list of str: The file paths of the files with merge conflicts.
        """
        return self._file_paths
    
    def get_responses(self):
        """
        Returns the responses (solutions to the merge conflicts) from the AI model.

        Returns:
            list of str: The responses from the AI model.
        """
        return self.responses
    
    def get_commit_msg(self):
        """
        Returns the commit message.

        Returns:
            str: The commit message.
        """
        return self.commit_msg

    def solve_merge_conflict(self):
        """
        Solves the merge conflicts in the Git repositories using the OpenAI API.

        This method first encodes the prompt to base64 and checks if it exists in the cache.
        If it does (cache hit), it retrieves the answer from the cache, decodes it from base64.
        If it doesn't (cache miss), it sends the prompt to the OpenAI API, gets the response,
        and updates the cache with the base64 encoded response.

        The method then appends the explanation and the resolved file content (code) from the response 
        to the explanations and responses lists respectively.

        Returns:
            dict: The response from the OpenAI API or the cache, which includes the explanation 
            and the resolved file content (code).
        """
        base64_prompt = encode_to_base64(self._prompt)
        if self._cache.lookup(base64_prompt):
            print("Cache hit!\n")
            cache_content = self._cache.get_answer(base64_prompt)
            response = decode_from_base64(cache_content)
            response = ast.literal_eval(response) #Prevent json.loads from throwing an error
        else:
            print("Cache miss!")
            response = json.loads(get_completion(self._prompt, type="json_object"))
            self._cache.update(
                base64_prompt,
                encode_to_base64(response)
                )                
        self.explanations += [response["explanation"]]
        self.responses += [response["code"]] # merge conflict resolved file content
        return response
    
    def make_commit_msg(self):
        """
        Generates a commit message based on the explanations provided by the AI model.

        This method constructs a commit prompt by appending each explanation from the explanations list 
        to the commit_prompt string. It then sends the commit_prompt to the OpenAI API and stores the 
        response as the commit message.

        The commit message is stored in the instance variable commit_msg.
        """
        commit_prompt = prompts.commit_prompt
        for i, explanation in enumerate(self.explanations):
            commit_prompt += "Explanation " + str(i) + ":\n"
            commit_prompt += explanation + "\n"
        self.commit_msg = get_completion(
            commit_prompt,
            model=os.environ["TEXT-DEPLOYMENT"],
            type="text"
            )

    def make_prompt(self, file_path: str, file_content:str) -> str:
        """
        Generates a prompt for the AI model based on the file path and content.

        This method appends the file path to the _file_paths list and formats the merge_prompt string 
        with the file content to create the prompt for the AI model. The prompt is stored in the 
        instance variable _prompt.

        Args:
            file_path (str): The path to the file with a merge conflict.
            file_content (str): The content of the file with a merge conflict.

        Returns:
            str: The prompt for the AI model.
        """
        self._file_paths += [file_path]
        self._prompt = prompts.merge_prompt.format(file_content=file_content)
        return self._prompt

    def __str__(self):
        """
        Returns a string representation of the Agent.

        This method constructs a string that starts with "Merged File_Paths:\n" and appends each file 
        path from the _file_paths list to the string. The string representation is used when the print 
        function is called on an instance of the Agent class.

        Returns:
            str: A string representation of the Agent.
        """
        out = "Merged File_Paths:\n"
        for file_path in self._file_paths:
            out += file_path + "\n"
        return out
        