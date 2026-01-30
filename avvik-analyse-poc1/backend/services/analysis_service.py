import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

deployment = "gpt-4.1"

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

def build_prompt(plan_text: str) -> str:
    return f"""
Oppgave:
Trekk ut følgende informasjon hvis den finnes i teksten:
- energiforbruk
- arealbruk
- maks_høyde_kote
- sykkelparkeringsplasser
- henssynssone

Regler:
- Hvis noe ikke finnes i teksten, sett verdien til null.
- Returner svaret KUN som gyldig JSON.

Format:
{
    {
    "energiforbruk": "...",
    "arealbruk": "...",
    "maks_høyde_kote": "...",
    "sykkelparkeringsplasser": "...",
    "hensynssone": "..."
    }
}

Her er teksten:
{plan_text}
"""

def extract_info_from_text(plan_text: str):
    prompt = build_prompt(plan_text)

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "Du returnerer kun gyldig JSON."},
            {"role": "user", "content": prompt}
        ],
        max_completion_tokens=200
    )

    raw = response.choices[0].message.content

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "Ugyldig JSON fra modellen", "raw": raw}