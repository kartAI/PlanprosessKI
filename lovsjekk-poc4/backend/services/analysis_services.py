#laster inn og importer biblioteker
import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

#Koble til modellen
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

#Valg av modell
deployment = "gpt-4.1"

#tom funskjon for prompt
def test():
    prompt = f"""

"""
    
    #konfgig ting
    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=300
    )

    return response.choices[0].message.content.strip()


