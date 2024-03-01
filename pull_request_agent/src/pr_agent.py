import openai
import os
import pull_request_agent.src.prompts as prompts

openai.api_key = os.environ["OPENAI_API_KEY"]
def get_completion(prompt, model="gpt-4-1106-preview", type="text"):
    """
    Sends a prompt to the OpenAI API and returns the AI"s response.
    """
    messages = [
        {
            "role": "system",
            "content": prompts.pr_system_prompt
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
