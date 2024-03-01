import openai
import os

openai.api_key = os.environ["OPENAI_API_KEY"]
def get_completion(prompt, model="gpt-4-1106-preview", type="text"):
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

class PRAgent:
    def __init__(self):
        pass