import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)


# Prompt som trekker ut formål, høyde, hensynssone og bevaringskrav 
def build_prompt(plan_text: str) -> str: 
    return f"""
Du får nå en tekst fra en reguleringsplan (planbestemmelse eller planbeskrivelse).

Oppgave:
Trekk ut følgende informasjon hvis den finnes i teksten:
- formål
- maksimal byggehøyde (meter)
- hensynssoner
- bevaringskrav

Regler:
- Hvis noe ikke finnes i teksten, sett verdien til null.
- Returner svaret KUN som gyldig JSON.
- Ikke skriv forklaringer, tekst eller kommentarer utenfor JSON.

Format:
{{
  "formål": "...",
  "maks_høyde": tall eller null,
  "hensynssone": "...",
  "bevaringskrav": "..."
}}

Her er teksten:
{plan_text}
"""

# Kall GPT-4.1-mini og returner JSON
async def extract_info_from_text(plan_text: str): 
    prompt = build_prompt(plan_text) 
    
    response = client.chat.completions.create( 
        model="gpt-4.1-mini", 
        messages=[{"role": "user", "content": prompt}], 
        max_tokens=2048 
    )

    raw_output = response.choices[0].message.content

    try: 
        return json.loads(raw_output) 
    except json.JSONDecodeError: 
        return {"error": "Ugyldig JSON fra GPT", "raw": raw_output}