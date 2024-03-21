import os
import httpx
from openai import AzureOpenAI

# Erstellen Sie den Client mit Ihren API-Schlüsseln und Endpunkten
client = AzureOpenAI(
    api_key="5c04a0b26b2a41c085db3013bcaa6c2d",
    api_version="2024-02-01",
    azure_endpoint="https://gcdm-ai-emea-poc-sweden.openai.azure.com",
    http_client=httpx.Client(
        proxies="http://proxy.ccc-ng-1.eu-central-1.aws.cloud.bmw:8080/"
    )
)

def get_completion(prompt, model="GCDM-EMEA-GPT4-1106", type="json_object"):
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
        temperature=0,
        response_format={"type": type}
    )
    return response.choices[0].message.content

# Testen Sie die Funktion mit einem Prompt
print(get_completion("Your prompt here, please answer with json format with any keys"))