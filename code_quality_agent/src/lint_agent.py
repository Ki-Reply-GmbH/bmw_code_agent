import subprocess
import re
import os
import json
import openai
from prompts import linter_prompt

openai.api_key = os.environ["OPENAI_API_KEY"]
def get_completion(prompt, model="gpt-4-1106-preview", type="json_object"):
    """
    Sends a prompt to the OpenAI API and returns the AI's response.
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
        temperature=0, # this is the degree of randomness of the model's output,
        response_format={"type": type}
    )
    return response.choices[0].message.content

class LintAgent:
    def __init__(self, directory, language):
        self.directory = directory
        self.raw_stats = ""
        self.tasks = []
        self.improved_code = []
        self.language = language

        self.check_code()
        self.create_tasks()

    def check_code(self):
        """
        Runs the appropriate linter on the directory and stores the output in raw_stats.
        """
        if self.language == 'python':
            result = subprocess.run(
                ["black", "--diff", self.directory],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
        elif self.language == 'java':
            result = subprocess.run(
                ["checkstyle", "-f", "xml", self.directory],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
        self.raw_stats = result.stdout.decode("utf-8")

    def create_tasks(self):
        """
        Extracts tasks from the raw output and stores them in the tasks list.
        Each task is a tuple where the first element is a file path and the second element is the task description.
        """
        pattern = r"--- (.*?)\s.*?@@.*?\n(.*?)would reformat"
        matches = re.findall(pattern, self.raw_stats, re.DOTALL)
        self.tasks = matches

    def improve_code(self):
        """
        Given a task, returns the improved code using the OpenAI API.
        """
        for task in self.tasks:
            file_path, task_description = task
            with open(file_path, "r") as file:
                code = file.read()
            linter_suggestions = task_description
            if self.language == 'python':
                prompt = py_prompt.format(code=code, linter_suggestions=linter_suggestions)
            elif self.language == 'java':
                prompt = java_prompt.format(code=code, linter_suggestions=linter_suggestions)
            print("Calling OpenAI API for " + file_path + "...")
            improved_code = get_completion(prompt)
            self.improved_code.append((file_path, improved_code))

    def write_changes(self):
        """
        Writes the improved code back to the files.
        """
        for path, improved_code in self.improved_code:
            improved_code = json.loads(improved_code)["improved_code"]
            with open(path, "w") as file:
                file.write(improved_code)

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
        for tup in self.improved_code:
            s += f"{tup[0]}\n"
            s += str(type(tup[1]))
            s += f"{tup[1]}\n".encode("utf-8").decode("unicode-escape")
        return s