import openai
import os
import pull_request_agent.src.prompts as prompts

openai.api_key = os.environ["OPENAI_API_KEY"]
def get_completion(
        prompt,
        system_prompt=prompts.pr_system_prompt,
        model="gpt-4",
        type="text"):
    """
    Sends a prompt to the OpenAI API and returns the AI"s response.
    """
    messages = [
        {
            "role": "system",
            "content": system_prompt
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

class PRAgent:
    def __init__(self):
        self.memory_merge_agent = {
            "files_changed": [],
            "code_changes": [],
            "commit_message": "",
        }
        self.memory_cq_agent = {
            "files_changed": [],
            "code_changes": [],
            "commit_message": "",
        }
        self.response = ""
        self.title = ""
    
    def get_summary(self):
        return self.response
    
    def get_title(self):
        return self.title

    def set_memory(self, agent, files_changed, code_changes, commit_message):
        if agent == "merge_agent":
            self.memory_merge_agent["files_changed"] = files_changed
            self.memory_merge_agent["code_changes"] = code_changes
            self.memory_merge_agent["commit_message"] = commit_message
        elif agent == "cq_agent":
            self.memory_cq_agent["files_changed"] = files_changed
            self.memory_cq_agent["code_changes"] = code_changes
            self.memory_cq_agent["commit_message"] = commit_message

    def make_summary(self):
        response = get_completion(
            prompts.pr_user_prompt.format(
                memory_merge_agent=self.memory_merge_agent,
                memory_cq_agent=self.memory_cq_agent
                )
            )
        self.response = response
    
    def make_title(self):
        response = get_completion(
            prompt=self.response,
            system_prompt=prompts.pr_title_system_prompt,
        )
        self.title = response

    def write_response(self):
        with open("response.txt", "w") as f:
            f.write(self.title + "\n")
            f.write(self.response)

    def __str__(self):
        return f"Merge Agent Memory: {self.memory_merge_agent}\nCode Quality Agent Memory: {self.memory_cq_agent}"