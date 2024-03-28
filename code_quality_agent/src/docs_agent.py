import code_quality_agent.src.prompts as prompts
import os
import ast
import re
import httpx
from openai import AzureOpenAI
from . import CodeQualityAgent
from code_quality_agent.src.file_retriever import FileRetriever

client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    http_client=httpx.Client(
        proxies=os.environ["HTTPS_PROXY"]
    )
)

def get_completion(prompt, model="GCDM-EMEA-GPT4-1106", type="json_object"):
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

class DocsAgent(CodeQualityAgent):
    """
    1. Pruefen der bestehenden Dokumentation (doc von code generieren und mit 
        bestehender Doc semantisch vergleichen)
    2. Falls ein unterschied besteht, dann entweder automatisch umschreiben 
        oder im PR vorschlagen.
    """
    def __init__(self, file_list, directory, language):
        super().__init__(file_list)
        self.directory = directory
        self.language = language
        self.existing_docstrings = []

    def write_docstrings(self):
        for file_path in self.file_list:
            _, extension = os.path.splitext(file_path)
    
    def 

    def extract_docstrings(self):
        """
        Extracts the docstrings from a file.

        Args:
            file_path (str): The file path.

        Returns:
            list of str: The docstrings.
        """
        # Get the mapping of file extensions to file paths
        file_retriever = FileRetriever(self.directory)
        file_mapping = file_retriever.get_mapping()

        # Currently only Java and Python are supported
        if self.language == "python":
            python_files = file_mapping.get("py", [])
            for file_path in python_files:
                docstrings = self.extract_pydoc(file_path)
                self.existing_docstrings.extend(docstrings)
        elif self.language == "java":
            java_files = file_mapping.get("java", [])
            for file_path in java_files:
                docstrings = self.extract_javadoc(file_path)
                self.existing_docstrings.extend(docstrings)
    
    def extract_pydoc(file_path):
        """
        Extracts the Python docstrings from a file.

        Args:
            file_path (str): The file path.

        Returns:
            list of str: The docstrings. Returns an empty list if no docstrings are found.
        """
        with open(file_path, "r") as file:
            module = ast.parse(file.read())

        docstrings = ast.get_docstring(module, clean=True)
        return docstrings if docstrings else []
    
    def extract_javadoc(file_path):
        """
        Extracts the Java docstrings from a file.

        Args:
            file_path (str): The file path.

        Returns:
            list of str: The docstrings. Returns an empty list if no docstrings are found.
        """
        with open(file_path, "r") as file:
            content = file.read()

        pattern = r"/\*\*(.*?)\*/"
        matches = re.findall(pattern, content, re.DOTALL)

        docstrings = []
        for match in matches:
            docstring = match.strip()
            docstrings.append(docstring)

        return docstrings