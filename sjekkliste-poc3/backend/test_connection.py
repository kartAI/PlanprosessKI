import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

print("AZURE_OPENAI_ENDPOINT:", os.getenv("AZURE_OPENAI_ENDPOINT"))
print("AZURE_OPENAI_API_KEY set:", bool(os.getenv("AZURE_OPENAI_API_KEY")))
print("AZURE_OPENAI_API_VERSION:", os.getenv("AZURE_OPENAI_API_VERSION"))

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

try:
    response = client.chat.completions.create(
        model="Mistral-Large-3",
        messages=[
            {"role": "user", "content": "What is the capital of France?"}
        ],
        max_tokens=20,
        temperature=0
    )
    print("Response:", response.choices[0].message.content)
except Exception as e:
    import traceback
    traceback.print_exc()