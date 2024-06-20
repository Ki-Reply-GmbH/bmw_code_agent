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
client = AzureOpenAI(api_key=os.getenv('OPENAI_API_KEY'), api_version=
    '2024-02-01', azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
    http_client=httpx.Client(proxies=os.environ['HTTPS_PROXY'], timeout=
    httpx.Timeout(600.0, read=600.0)))


def get_completion(prompt, model=os.environ['JSON-DEPLOYMENT'], type=
    'json_object'):
    """
    Sends a prompt to the OpenAI API and returns the AI"s response.
    """
    messages = [{'role': 'system', 'content':
        'You are a system designed to improve code quality.'}, {'role':
        'user', 'content': prompt}]
    response = client.chat.completions.create(model=model, messages=
        messages, temperature=0, response_format={'type': type})
    return response.choices[0].message.content


class DocsAgent(CodeQualityAgent):
    """
    A class designed to automate the generation and management of documentation for source code files. 
    DocsAgent handles various tasks such as initializing documentation environments, generating docstrings, 
    and writing changes to source files. It supports multiple programming languages and manages both the detection 
    and insertion of missing docstrings in code files.

    Attributes:
        directory (str): Directory containing the files to be documented.
        language (str): Programming language of the files.
        _existing_docstrings (list): List of existing docstrings found in the files.
        _responses (list): List of responses from the documentation generation process.

    Methods:
        __init__(self, file_list, directory, language): Initializes a new DocsAgent instance.
        make_docstrings(self): Generates and writes docstrings for files in the specified directory.
        _write_changes(self, file_path, code): Writes the updated source code with docstrings to the file.
        _can_add_docstrings(self, file_path): Checks if docstrings can be added to a file.
        _extract_docstrings(self): Extracts existing docstrings from files based on the programming language.
        _extract_pydoc(self, file_path): Extracts Python docstrings from a file.
        _extract_javadoc(self, file_path): Extracts JavaDoc comments from a Java file.
    """
    LOGGER.debug('~~~~~~ DocsAgent ~~~~~~')

    def __init__(self, file_list, directory, language):
        """
        Initialize a DocsAgent instance for managing and generating documentation.

        Parameters:
            file_list (list): A list of file paths to process.
            directory (str): The directory where the files are located.
            language (str): The programming language of the files (e.g., 'python', 'java').

        Attributes:
            directory (str): Directory containing the files to be documented.
            language (str): Programming language of the files.
            _existing_docstrings (list): List of existing docstrings found in the files.
            _responses (list): List of responses from the documentation generation process.
        """
        super().__init__(file_list)
        self.directory = directory
        self.language = language
        self._existing_docstrings = []
        self._responses = []
        self._extract_docstrings()

    def make_docstrings(self):
        """
        Automatically generates and writes docstrings for source code files in the specified directory and language.

        This method iterates over each file in the file list, checks if docstrings can be added, and if so, reads the file content,
        generates docstrings using an AI model, and writes the changes back to the file. It logs the response for debugging purposes.
        """
        for file_path in self.file_list:
            full_file_path = os.path.join(self.directory, file_path)
            if self._can_add_docstrings(full_file_path):
                with open(full_file_path, 'r') as file:
                    file_content = file.read()
                response = get_completion(prompts.docs_prompt.format(
                    language=self.language, docstrings=self.
                    _existing_docstrings, code=file_content))
                LOGGER.debug('Respne:\n' + str(response))
                self._responses.append(response)
                self._write_changes(full_file_path, response[
                    'documented_source_code'])

    def _write_changes(self, file_path, code):
        """
        Writes the updated source code with added docstrings to the specified file.

        This method takes a file path and the modified source code as input. It then
        opens the specified file in write mode and overwrites it with the new code that
        includes docstrings.

        Args:
            file_path (str): The path to the file where the code will be written.
            code (str): The complete source code including newly added docstrings.
        """
        with open(file_path, 'w') as file:
            file.write(code)

    def _can_add_docstrings(self, file_path):
        """
        Determines if docstrings can be added to the specified file based on its language and extension.

        This method checks if the file specified by `file_path` is in the supported language and has the appropriate file extension.
        It then extracts existing docstrings from the file to determine if any are missing, allowing for the addition of new docstrings.

        Parameters:
            file_path (str): The path to the file to check.

        Returns:
            bool: True if docstrings can be added, False otherwise.
        """
        _, extension = os.path.splitext(file_path)
        LOGGER.debug('long file path = ' + file_path)
        if self.language == 'python' and extension == '.py':
            docstrings = self._extract_pydoc(file_path)
        elif self.language == 'java' and extension == '.java':
            docstrings = self._extract_javadoc(file_path)
        else:
            return False
        return len(docstrings) == 0

    def _extract_docstrings(self):
        """
        Extracts existing docstrings from the source files in the specified directory based on the language attribute.

        This method iterates over the files in the directory, filtering them by the language attribute (currently supports 'python' and 'java'). It uses language-specific methods to extract docstrings from these files and stores them in the _existing_docstrings list.
        """
        file_retriever = FileRetriever(self.directory)
        file_mapping = file_retriever.get_mapping()
        if self.language == 'python':
            python_files = file_mapping.get('py', [])
            for file_path in python_files:
                docstrings = self._extract_pydoc(file_path)
                self._existing_docstrings.extend(docstrings)
        elif self.language == 'java':
            java_files = file_mapping.get('java', [])
            for file_path in java_files:
                docstrings = self._extract_javadoc(file_path)
                self._existing_docstrings.extend(docstrings)

    def _extract_pydoc(self, file_path):
        """
        Extracts Python docstrings from the specified file.

        This method reads the content of a Python file, parses it to create an AST (Abstract Syntax Tree),
        and then extracts the module-level docstring if it exists.

        Args:
            file_path (str): The path to the Python file from which to extract the docstring.

        Returns:
            list: A list containing the extracted docstring, or an empty list if no docstring is found.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            module = ast.parse(file.read())
        docstrings = ast.get_docstring(module, clean=True)
        return docstrings if docstrings else []

    def _extract_javadoc(self, file_path):
        """
        Extracts all JavaDoc comments from a given Java source file.

        This method reads the content of a Java file, searches for all JavaDoc comments
        using a regular expression that matches the JavaDoc pattern, and returns a list
        of these docstrings.

        Parameters:
            file_path (str): The path to the Java file from which to extract JavaDoc comments.

        Returns:
            list: A list of extracted JavaDoc strings, stripped of leading and trailing whitespace.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        pattern = '/\\*\\*(.*?)\\*/'
        matches = re.findall(pattern, content, re.DOTALL)
        docstrings = []
        for match in matches:
            docstring = match.strip()
            docstrings.append(docstring)
        return docstrings
