import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI
import re
from pathlib import Path
from read_pdf import read_pdf

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
        if not line:
            continue

        if "•" in line:
            parts = [p.strip() for p in line.split("•") if p.strip()]
            if parts:
                head = parts[0]
                if re.match(r"^\d+(?:\.\d+)?\s+", head):
                    combined.append(head)
                    bullet_parts = parts[1:]
                else:
                    bullet_parts = parts
                for bullet in bullet_parts:
                    combined.append(bullet)
            continue

        numbered_matches = re.findall(
            r"\b\d+(?:\.\d+)?\s+[^\d]+?(?=\s+\d+(?:\.\d+)?\s+|$)",
            line
        )
        if numbered_matches:
            combined.extend([m.strip() for m in numbered_matches])
            continue

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

KRAV FOR AT ET PUNKT ER OPPFYLT:
- Punktet er KUN "oppfylt" hvis dokumentet inneholder en EGEN OVERSKRIFT eller seksjon som eksplisitt matcher punktet ordrett (eller nesten ordrett), OG denne overskriften har tilhørende tekst under seg.
- Det er IKKE nok at temaet nevnes i forbifarten under et annet punkt.
- Det er IKKE nok at dokumentet omtaler noe som ligner.
- Det er IKKE nok at dokumentet omtaler temaet i en annen sammenheng.
- Hvis overskriften ikke finnes, eller ikke har tekst under seg, skal punktet være "ikke oppfylt".

GENERELLE REGLER:
- Du SKAL returnere alle punktene i sjekklisten, i samme rekkefølge.
- Du SKAL bruke hvert punkt ordrett, uten endringer, uten sammenslåing, uten utelatelser.
- Du skal KUN bruke tekst som står i DOKUMENT-seksjonen nedenfor.
- Du skal IKKE tolke, IKKE anta, IKKE vurdere kvalitet, IKKE bruke indirekte eller relatert informasjon.
- Du skal IKKE bruke semantisk likhet.
- Du skal IKKE bruke tekst som bare ligner.
- Du skal IKKE bruke tekst fra andre punkter som “bevis”.
- Du skal IKKE gjette.
- Hvis du er usikker, skal du svare "ikke oppfylt".
- Alle punktene og under punktene skal stå hver for seg, og vurderes hver for seg.

For hvert punkt i sjekklisten skal du:
- Sette "status" til "oppfylt" eller "ikke oppfylt".
- Du skal gi en kort forklaring på hvorfor status er satt.

Du SKAL returnere KUN gyldig JSON i dette formatet:

{{
    "resultat": [
        {{
        "punkt": "...",
        "status": "oppfylt" eller "ikke oppfylt",
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

if __name__ == "__main__":
    # Finn første (og eneste) opplastede fil
    uploaded_files = list(uploads.glob("*.pdf"))

    if not uploaded_files:
        raise FileNotFoundError("Ingen PDF funnet i uploads-mappen")

    path = uploaded_files[0]

    document_text = read_pdf(str(path))

    # Kjør sjekk
    resultat = check_document_against_checklist(document_text, checklist_points)

    print(resultat)



