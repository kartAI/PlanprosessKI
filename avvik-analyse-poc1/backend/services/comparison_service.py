import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

deployment = "gpt-5.1-chat"

client = OpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

def compare_documents(planbestemmelse, planbeskrivelse, plankart_json):
    prompt = f"""
    Sammenlign følgende tre dokumenter:
    1. Planbestemmelse: {planbestemmelse}
    2. Planbeskrivelse: {planbeskrivelse}
    3. Plankart (JSON): {plankart_json}

    Finn og oppsummer alle avvik, mangler og forskjeller mellom dokumentene. Returner kun en kortfattet Markdown-tabell med kolonnene: Element 
    | Avvik | Notat.
    """
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "Du er en ekspert på plansammenligning. Returner kun en Markdown-tabell."},
            {"role": "user", "content": prompt}
        ],
        max_completion_tokens=2000
    )
    return response.choices[0].message.content