import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI
import re
from pathlib import Path
from ..read_pdf import read_pdf

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

deployment = "gpt-4.1"

# ekstraherer numererte punkter og underpunkter fra et dokument
def extract_checklist_points(text: str) -> list[str]:

    # Kombiner i rekkefølge slik de står i dokumentet
    # (regex alene bevarer ikke rekkefølgen)
    combined = []
    for line in text.splitlines():
        line = line.strip()
        if re.match(r"\d+\.\d+\s+", line):
            combined.append(line)
        elif line.startswith("•"):
            combined.append(line[1:].strip())  # fjern •

    return combined

def load_checklist_from_sjekklister(filename: str) -> str:
    sjekklister = Path(__file__).parent.parent / "sjekklister"
    path = sjekklister / filename
    return read_pdf(str(path))



checklist_text = load_checklist_from_sjekklister("sjekkliste_for_planbeskrivelse_bokm_mal.pdf")
checklist_points = extract_checklist_points(checklist_text)



def check_document_against_checklist(document_text: str, checklist: list[str]):
    checklist_joined = "\n".join([f"- {p}" for p in checklist])

    prompt = f"""
Du skal evaluere et dokument opp mot en sjekkliste.

VIKTIG:
- Bruk hvert sjekkpunkt ORDRETT slik det står i listen.
- Ikke slå sammen punkter.
- Ikke legg til nye punkter.
- For hvert punkt skal du si om det er OPPFYLT eller IKKE OPPFYLT.
- Returner KUN gyldig JSON i dette formatet:

{{
    "resultat": [
    {{
        "punkt": "...",
        "status": "oppfylt" eller "ikke oppfylt"
    }}
    ]
}}

SJEKKLISTE:
{checklist_joined}

DOKUMENT:
{document_text}
"""

    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=800
    )

    raw = response.choices[0].message.content

    try:
        return json.loads(raw)
    except Exception:
        return {
            "error": "Ugyldig JSON fra KI",
            "raw": raw
        }

# Les dokumentet som skal sjekkes
uploads = Path(__file__).parent.parent / "uploads"
path = uploads / "planbeskrivelse_m.pdf"

document_text = read_pdf(str(path))

# Kjør sjekk
resultat = check_document_against_checklist(document_text, checklist_points)

print(resultat)



