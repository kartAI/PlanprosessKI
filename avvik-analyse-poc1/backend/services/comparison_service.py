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

def compare_documents(doc1_text, doc2_text, doc3_text, doc1_name="Dokument 1", doc2_name="Dokument 2", doc3_name="Dokument 3"):
    """
    Sammenligner tre dokumenter og returnerer avvik og manglende informasjon.
    """
    
    prompt = f"""Du er en ekspert på dokumentsammenlikning. Sammenlign følgende tre dokumenter og gi en KORT og PRESIS tilbakemelding om hva som MANGLER.

KRAV TIL SVAR:
- Lever KUN én tabell over manglende informasjon.
- Ikke inkluder avvik eller samstemte områder.
- Tabellformat (Markdown):
    Kolonner: Tema | Mangler i (Dok1/Dok2/Dok3) | Sitat/henvisning (kort) | Konsekvens (kort)
- For hver rad: oppgi kort sitat (1–2 setninger) fra relevant dokument der informasjonen burde vært/nevnes.
- Ikke gjett. Hvis det ikke fremgår i utdraget, skriv "Ikke synlig i utdraget".
- Avslutt med en kort oppsummering (maks 2 setninger).

STRUKTUR:
1) Tabell: Manglende informasjon
2) Oppsummering

DOKUMENT 1 ({doc1_name}):
{doc1_text[:3000]}  # Begrenset til 3000 tegn per dokument for å spare tokens

DOKUMENT 2 ({doc2_name}):
{doc2_text[:3000]}

DOKUMENT 3 ({doc3_name}):
{doc3_text[:3000]}
"""
    
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "Du er en juridisk/teknisk dokumentanalytiker som spesialiserer seg på å identifisere avvik."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_completion_tokens=2000
    )
    
    return response.choices[0].message.content