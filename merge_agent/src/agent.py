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
import openai
import pandas as pd
import json
import ast
from github import Github, Auth
import prompts
from functions import encode_to_base64, decode_from_base64
from cache import Cache

EXPLANATION, ANSWER = 0, 0
CODE, COMMIT_MSG = 1, 1
tmp_path = os.path.join(os.path.dirname(__file__), ".tmp")
git_access_token = os.environ["GIT_ACCESS_TOKEN"]
openai.api_key = os.environ["OPENAI_API_KEY"]
def get_completion(prompt, model="gpt-4-1106-preview", type="text"):
    """
    Sends a prompt to the OpenAI API and returns the AI's response.
    """
    messages = [
        {
            "role": "system",
            "content": "You are a system designed to solve GitHub merge conflicts."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    response = openai.OpenAI().chat.completions.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output,
        response_format={"type": type}
    )
    return response.choices[0].message.content

class Agent():
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
        self.commit_msg = get_completion(commit_prompt)

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
    
    def write_responses(self):
        """
        Writes the AI's responses (solutions to the merge conflicts) back to the files.

        This method iterates over the _file_paths list and for each file path, it opens the corresponding 
        file in the downstream repository in write mode and writes the corresponding response from the 
        responses list to the file.

        Note: The method assumes that the order of the file paths in _file_paths matches the order of 
        the responses in responses.
        """
        for i, file_path in enumerate(self._file_paths):
            with open(os.path.join(tmp_path, file_path), 'w') as file:
                file.write(self.responses[i])

    def git_actions(self):
        """
        Performs Git actions such as add, commit, and push.

        This method performs the following Git actions in the downstream repository:
        - Adds the files with the resolved merge conflicts to the staging area.
        - Commits the changes with the commit message generated by the AI model.
        - Pushes the changes to the remote repository, setting the upstream branch to the active branch.
        """
        self._repo.git.add(self._file_paths)
        self._repo.git.commit("-m", self.commit_msg)
        self._repo.git.push("--set-upstream", "origin", self._repo.active_branch.name)

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
        