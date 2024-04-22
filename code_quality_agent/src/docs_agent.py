import code_quality_agent.src.prompts as prompts
import os
import ast
import re
import httpx
import logging
from openai import AzureOpenAI
from . import CodeQualityAgent
from code_quality_agent.src.file_retriever import FileRetriever

LOGGER = logging.getLogger(__name__)

client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    http_client=httpx.Client(
        proxies=os.environ["HTTPS_PROXY"],
        timeout=httpx.Timeout(300.0, read=300.0)
    )
)

def get_completion(prompt, model=os.environ["JSON-DEPLOYMENT"], type="json_object"):
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
    LOGGER.debug("~~~~~~ DocsAgent ~~~~~~")
    def __init__(self, file_list, directory, language):
        super().__init__(file_list)
        self.directory = directory
        self.language = language
        self._existing_docstrings = []
        self._responses = []

        self._extract_docstrings()

    def make_docstrings(self):
        for file_path in self.file_list:
            full_file_path = os.path.join(self.directory, file_path)
            if self._can_add_docstrings(full_file_path):
                with open(full_file_path, "r") as file:
                    file_content = file.read()
                response = get_completion(
                    prompts.docs_prompt.format(
                        language=self.language,
                        docstrings=self._existing_docstrings,
                        code=file_content
                    )
                )
                LOGGER.debug("Respne:\n" + str(response))
                self._responses.append(response)
                self._write_changes(full_file_path, response["documented_source_code"])
    
    def _write_changes(self, file_path, code):
        with open(file_path, "w") as file:
            file.write(code)
    
    def _can_add_docstrings(self, file_path):
        """
        Checks if docstrings can be added to a file.

        Args:
            file_path (str): The file path.

        Returns:
            bool: True if docstrings can be added, False otherwise.
        """
        _, extension = os.path.splitext(file_path)
        LOGGER.debug("long file path = " + file_path)

        if self.language == "python" and extension == ".py":
            docstrings = self._extract_pydoc(file_path)
        elif self.language == "java" and extension == ".java":
            docstrings = self._extract_javadoc(file_path)
        else:
            return False

        return len(docstrings) == 0

    def _extract_docstrings(self):
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
                docstrings = self._extract_pydoc(file_path)
                self._existing_docstrings.extend(docstrings)
        elif self.language == "java":
            java_files = file_mapping.get("java", [])
            for file_path in java_files:
                docstrings = self._extract_javadoc(file_path)
                self._existing_docstrings.extend(docstrings)
    
    def _extract_pydoc(self, file_path):
        """
        Extracts the Python docstrings from a file.

        Args:
            file_path (str): The file path.

        Returns:
            list of str: The docstrings. Returns an empty list if no docstrings are found.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            module = ast.parse(file.read())

        docstrings = ast.get_docstring(module, clean=True)
        return docstrings if docstrings else []
    
    def _extract_javadoc(self, file_path):
        """
        Extracts the Java docstrings from a file.

        Args:
            file_path (str): The file path.

        Returns:
            list of str: The docstrings. Returns an empty list if no docstrings are found.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        pattern = r"/\*\*(.*?)\*/"
        matches = re.findall(pattern, content, re.DOTALL)

        docstrings = []
        for match in matches:
            docstring = match.strip()
            docstrings.append(docstring)

        return docstrings