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

def compare_documents(doc1_text, doc2_text, doc3_text, doc1_name="Planbestemmelse", doc2_name="Planbeskrivelse", doc3_name="Plankart"):
    """
    Sammenligner tre dokumenter og returnerer avvik og manglende informasjon.
    """
    
    prompt = f"""Du er en ekspert på dokumentsammenlikning. Sammenlign følgende tre dokumenter.

DOKUMENTNAVN:
- planbestemmelse = {doc1_name}
- planbeskrivelse = {doc2_name}
- plankart = {doc3_name}

KRAV TIL SVAR:

TABELL - MANGLER OG AVVIK:
Kolonner: Element | Mangler i | Avvik | Notat
- Element: Hvilke punkter gjelder det?
- Mangler i: Hvilke dokumenter som mangler disse elementene?
- Avvik: Konkrete avvik mellom dokumentene?
- Notat: Kort konsekvens eller merknad

REGLER:
- Bruk bare Markdown-tabellformat
- Hold svar kort og presist
- Ta kun med elementer der det faktisk finnes avvik eller mangler
- Ikke ta med elementer som er like i alle dokumenter
- Avslutt med en kort oppsummering etter tabellen

DOKUMENT 1 ({doc1_name}):
{doc1_text[:3000]}

DOKUMENT 2 ({doc2_name}):
{doc2_text[:3000]}

DOKUMENT 3 ({doc3_name}):
{doc3_text[:3000]}
"""
    
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "Du er en juridisk/teknisk dokumentanalytiker som spesialiserer seg på å identifisere avvik. Returner alltid en Markdown-tabell som spesifisert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_completion_tokens=2000
    )
    
    return response.choices[0].message.content