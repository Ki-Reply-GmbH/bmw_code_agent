import subprocess
import re
import os
import json
from collections import defaultdict
import code_quality_agent.src.prompts as prompts
import httpx
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version="2023-12-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    http_client=httpx.Client(
        proxies=os.environ["HTTPS_PROXY"]
    )
)

def get_completion(prompt, model=os.getenv("GCDM-EMEA-GPT-4-1006"), type="json_object"):
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

class LintAgent:
    def __init__(self, directory, language):
        self.directory = directory
        self.raw_stats = ""
        self.tasks = []
        self.improved_source_code = []
        self.language = language
        self.commit_msg = ""

        self.check_code()
        self.create_tasks()

    def get_commit_msg(self):
        """
        Returns the commit message.

        Returns:
            str: The commit message.
        """
        return self.commit_msg

    def get_file_paths(self):
        """
        Returns the file paths of the files with merge conflicts.

        Returns:
            list of str: The file paths of the files with merge conflicts.
        """
        file_paths = []
        for task, _ in self.tasks:
            file_paths.append(task)
        return file_paths

    def get_responses(self):
        """
        Returns the file paths of the files with merge conflicts.

        Returns:
            list of str: The file paths of the files with merge conflicts.
        """
        responses = []
        for _, response in self.tasks:
            responses.append(response)
        return responses

    def check_code(self):
        """
        Runs the appropriate linter on the directory and stores the output in raw_stats.
        """
        if self.language == "python":
            result = subprocess.run(
                ["black", "--diff", self.directory],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
                )
            self.raw_stats = result.stdout.decode("utf-8")
        elif self.language == "java":
            current_dir = os.path.dirname(os.path.realpath(__file__))
            pmd_path = os.path.join(current_dir, "../../pmd-bin-7.0.0-rc4/bin/pmd")
            result = subprocess.run(
                [os.path.join(
                    current_dir,
                    pmd_path
                    ),
                 "check",
                 "-d", self.directory,
                 "-R", "rulesets/java/quickstart.xml"],  #TODO env erstellen
                capture_output=True,
                text=True
                )
            self.raw_stats = result.stdout
        elif self.language == "java-local":
            result = subprocess.run(
                ["C:\\pmd-bin-7.0.0-rc4\\bin\\pmd.bat",
                 "check",
                 "-d", self.directory,
                 "-R", "rulesets/java/quickstart.xml"],  #TODO env erstellen
                capture_output=True,
                text=True
                )
            self.raw_stats = result.stdout

    def create_tasks(self):
        """
        Extracts tasks from the raw output and stores them in the tasks list.
        Each task is a tuple where the first element is a file path and the second element is the task description.
        """
        if self.language == "python":
            pattern = r"--- (.*?)\s.*?@@.*?\n(.*?)would reformat"
            matches = re.findall(pattern, self.raw_stats, re.DOTALL)
            self.tasks = matches
        elif self.language == "java" or self.language == "java-local":
            lines = self.raw_stats.split("\n")
            # Dictionary verwenden, damit kein Dateipfad mehrfach vorkommt.
            tmp_dict = defaultdict(list)
            for line in lines:
                match = re.match(r"(.*\.java):\d+:\s+(.*)", line)
                if match:
                    directory, task = match.groups()
                    tmp_dict[directory].append(task)
            # Dictionary in Liste von Tupeln umwandeln
            self.tasks = [(k, "\n".join(v)) for k, v in tmp_dict.items()]

    def improve_code(self):
        """
        Given a task, returns the improved code using the OpenAI API.
        """
        for task in self.tasks:
            file_path, task_description = task
            with open(file_path, "r") as file:
                code = file.read()
            linter_suggestions = task_description
            prompt = prompts.lint_prompt.format(source_code=code, linter_suggestions=linter_suggestions)
            print("Calling OpenAI API for " + file_path + "...")
            print(prompt)
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            improved_source_code = get_completion(prompt)
            self.improved_source_code.append((file_path, improved_source_code))

    def write_changes(self):
        """
        Writes the improved code back to the files.
        """
        for path, improved_source_code in self.improved_source_code:
            improved_source_code = json.loads(improved_source_code)["improved_source_code"]
            with open(path, "w") as file:
                file.write(improved_source_code)

    def make_commit_msg(self):
        """
        Generates a commit message based on the explanations provided by the AI model.

        This method constructs a commit prompt by appending each explanation from the explanations list 
        to the commit_prompt string. It then sends the commit_prompt to the OpenAI API and stores the 
        response as the commit message.

        The commit message is stored in the instance variable commit_msg.
        """
        tasks = ""
        for path, improved_source_code in self.improved_source_code:
            tasks += path + ":\n"
            tasks += str(improved_source_code) + "\n"
        print("Commit Prompt: " + prompts.commit_prompt.format(tasks=tasks))
        self.commit_msg = get_completion(prompts.commit_prompt.format(tasks=tasks), type="text")

    def __str__(self):
        s = "Raw Stats:\n"
        s += self.raw_stats
        s = s.replace("\\U0001f4a5", "💥")
        s = s.replace("\\U0001f494", "💔")
        s = s.replace("\\U0001f370", "🍰")
        s = s.replace("\\u2728", "✨")
        s += "\nTasks:\n"
        for tup in self.tasks:
            s += f"{tup[0]}\n"
            s += f"{tup[1]}\n".encode("utf-8").decode("unicode-escape")
        s += "\nImproved Code:\n"
        for tup in self.improved_source_code:
            s += f"{tup[0]}\n"
            s += str(type(tup[1]))
            s += f"{tup[1]}\n".encode("utf-8").decode("unicode-escape")
        return s