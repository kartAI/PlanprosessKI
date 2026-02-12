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
    combined = []
    for line in text.splitlines():
        line = line.strip()

        # Hovedpunkter: 2 Bakgrunn, 3 Planprosessen, 4 Planstatus ...
        if re.match(r"^\d+\s+[^\n]+", line):
            combined.append(line)

        # Underpunkter: 2.1 Hensikten med planen, 4.1 Overordnede planer
        elif re.match(r"^\d+\.\d+\s+[^\n]+", line):
            combined.append(line)

        # Bulletpunkter: • Fylkeskommunale planer
        elif line.startswith("•"):
            combined.append(line.lstrip("•").strip())

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

Obligatoriske regler (du skal følge alle nøyaktig):
- Du SKAL returnere alle punktene i sjekklisten, i samme rekkefølge.
- Du SKAL bruke hvert punkt ordrett, uten endringer, uten sammenslåing, uten utelatelser.
- Du skal KUN sjekke om dokumentet inneholder tekst som eksplisitt nevner eller direkte beskriver temaet i punktet.
- Du skal IKKE tolke, IKKE anta, IKKE vurdere kvalitet, IKKE bruke indirekte eller relatert informasjon.
- Du skal IKKE bruke semantisk likhet. Hvis teksten ikke eksplisitt støtter punktet, skal du svare "ikke oppfylt".
- Et punkt er "oppfylt" hvis dokumentet har tekst som eksplisitt eller direkte beskriver temaet i punktet.
- Et punkt er "ikke oppfylt" hvis dokumentet ikke har slik tekst.
- Hvis du er usikker, skal du svare "ikke oppfylt".
- Hvis noe er uklart, skal du svare "ikke oppfylt".
- Du SKAL returnere alle punktene, selv om ingen av dem finnes i dokumentet.

For hvert punkt i sjekklisten skal du:
- Sette "status" til "oppfylt" eller "ikke oppfylt".
- Hvis status er "oppfylt", SKAL du fylle ut "bevis" med eksakt tekst fra dokumentet som viser at punktet er oppfylt.
- Hvis status er "ikke oppfylt", skal "bevis" være en tom streng.
- Du SKAL alltid gi en kort "forklaring" på hvorfor du satte den statusen.

Du SKAL returnere KUN gyldig JSON i dette formatet:

{{
    "resultat": [
        {{
        "punkt": "...",
        "status": "oppfylt" eller "ikke oppfylt",
        "bevis": "eksakt tekst fra dokumentet, eller tom streng",
        "forklaring": "kort forklaring på hvorfor status er satt"
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
    max_completion_tokens=2000,
    temperature=0.1
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



