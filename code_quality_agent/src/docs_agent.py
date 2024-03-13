import code_quality_agent.src.prompts as prompts
import os
import openai
import ast
import re

openai.api_key = os.environ["OPENAI_API_KEY"]
def get_completion(prompt, model="gpt-4-1106-preview", type="json_object"):
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
    response = openai.OpenAI().chat.completions.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model"s output,
        response_format={"type": type}
    )
    return response.choices[0].message.content

class DocsAgent:
    """
    1. Pruefen der bestehenden Dokumentation (doc von code generieren und mit 
        bestehender Doc semantisch vergleichen)
    2. Falls ein unterschied besteht, dann entweder automatisch umschreiben 
        oder im PR vorschlagen.
    """
    def __init__(self):
        pass

    def extract_docstrings(self, file_paths):
        """
        Extracts the docstrings from a file.

        Args:
            file_path (str): The file path.

        Returns:
            list of str: The docstrings.
        """
        pass
    
    def extract_pydoc(file_path):
        with open(file_path, "r") as file:
            module = ast.parse(file.read())

        docstrings = ast.get_docstring(module, clean=True)
        return docstrings
    
    def extract_javadoc(file_path):
        with open(file_path, "r") as file:
            content = file.read()

        pattern = r"/\*\*(.*?)\*/"
        matches = re.findall(pattern, content, re.DOTALL)

        docstrings = []
        for match in matches:
            docstring = match.strip()
            docstrings.append(docstring)

        return docstrings