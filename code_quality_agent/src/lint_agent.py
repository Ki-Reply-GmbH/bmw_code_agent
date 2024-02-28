import subprocess
import re
import os
import json
import openai
from prompts import py_prompt

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
    def __init__(self, direcory):
        self.direcory = direcory
        self.raw_python_stats = ""
        self.python_tasks = []
        self.improved_py_code = []

        self.check_python()
        self.create_py_tasks()

    def check_python(self):
        """
        Runs the 'black' Python linter on the directory and stores the output in raw_python_stats.
        """
        result = subprocess.run(
            ["black", "--diff", self.direcory],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
            )
        self.raw_python_stats = result.stdout.decode("utf-8")

    def create_py_tasks(self):
        """
        Extracts tasks from the raw output and stores them in the python_tasks list.
        Each task is a tuple where the first element is a file path and the second element is the task description.
        """
        pattern = r"--- (.*?)\s.*?@@.*?\n(.*?)would reformat"
        matches = re.findall(pattern, self.raw_python_stats, re.DOTALL)
        self.python_tasks = matches
    
    def improve_py_code(self):
        """
        Given a task, returns the improved code using the OpenAI API.
        """
        for task in self.python_tasks:
            file_path, task_description = task
            with open(file_path, "r") as file:
                python_code = file.read()
            linter_suggestions = task_description
            prompt = py_prompt.format(python_code=python_code, linter_suggestions=linter_suggestions)
            print("Calling OpenAI API for " + file_path + "...")
            improved_code = get_completion(prompt)
            self.improved_py_code.append((file_path, improved_code))

    def write_changes(self):      
        for path, improved_code in self.improved_py_code:
            improved_code = json.loads(improved_code)["improved_python_code"]
            with open(path, "w") as file:
                file.write(improved_code)

    def __str__(self):
        s = "Raw Python Stats:\n"
        s += self.raw_python_stats
        s = s.replace("\\U0001f4a5", "💥")
        s = s.replace("\\U0001f494", "💔")
        s = s.replace("\\U0001f370", "🍰")
        s = s.replace("\\u2728", "✨")
        s += "\nPython Tasks:\n"
        for tup in self.python_tasks:
            s += f"{tup[0]}\n"
            s += f"{tup[1]}\n".encode("utf-8").decode("unicode-escape")
        s += "\nImproved Code:\n"
        for tup in self.improved_py_code:
            s += f"{tup[0]}\n"
            s += str(type(tup[1]))
            s += f"{tup[1]}\n".encode("utf-8").decode("unicode-escape")
        return s