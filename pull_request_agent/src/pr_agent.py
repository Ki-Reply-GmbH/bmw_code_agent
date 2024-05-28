import pull_request_agent.src.prompts as prompts
import openai

def get_completion(prompt, model="GCDM-EMEA-GPT4", type="text"):
    """
    Sends a prompt to the OpenAI API and returns the AI"s response.
    """
    messages = [
        {
            "role": "system",
            "content": "You are a system designed to write comments for a GitHub Pull Request."
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

class PRAgent:
    def __init__(self, json_model="GCDM-EMEA-GPT4-1106", text_model="GCDM-EMEA-GPT4"):
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

        self.json_model = json_model
        self.text_model = text_model
    
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
                ),
            model=self.text_model
            )
        self.response = response
    
    def make_title(self):
        response = get_completion(
            prompts.pr_title_system_prompt.format(
                prev_responses=self.response
            ),
            model=self.text_model
        )
        self.title = response

    def write_response(self):
        with open("response.txt", "w") as f:
            f.write(self.title + "\n")
            f.write(self.response)

    def report_error(self, error_message):
        self.response = error_message

    def __str__(self):
        return f"Merge Agent Memory: {self.memory_merge_agent}\nCode Quality Agent Memory: {self.memory_cq_agent}"