import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

model="gpt-5-mini"
deployment="gpt-5-mini"

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)


# Prompt som trekker ut informasjon
def build_prompt(plan_text: str) -> str: 
    return f"""
Du får nå en tre pdf-filer fra et planforslag

Oppgave:
Trekk ut følgende informasjon hvis den finnes i teksten:
- formål
- maksimal byggehøyde (meter)
- hensynssoner
- bevaringskrav
- arealbruk

Regler:
- Hvis noe ikke finnes i teksten, sett verdien til null.
- Returner svaret KUN som gyldig JSON.
- Ikke skriv forklaringer, tekst eller kommentarer utenfor JSON.

Format:
{{
  "formål": "...",
  "maks_høyde": tall eller null,
  "hensynssoner": "...",
  "bevaringskrav": "...",
  "arealbruk": "..."
}}

Her er teksten:
{plan_text}
"""

# Kall GPT-5.1-mini og returner JSON
def extract_info_from_text(plan_text: str): 
    prompt = build_prompt(plan_text) 
    
    response = client.chat.completions.create( 
        
        messages=[
            {
                "role": "system",
                "content": "Du returnere kun gyldig JSON"
            },
            {
                "role": "user",
                "content": prompt
            }
            ], 
        max_token=2000,
        temperature=0,
        model=deployment
    )

    raw = response.choices[0].message.content

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "Ugyldig JSON fra modellen", "raw": raw}

    