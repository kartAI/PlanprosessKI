import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import re
from pathlib import Path
from read_pdf import read_pdf

load_dotenv()


client = OpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
)
deployment = "gpt-5.1-chat"
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
def clean_json_from_ai(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```") and raw.endswith("```"):
        raw = raw[3:-3].strip()
    if (raw.startswith("'") and raw.endswith("'")) or (raw.startswith('"') and raw.endswith('"')):
        inner = raw[1:-1].strip()
        if inner.startswith("{") and inner.endswith("}"):
            raw = inner
    raw = raw.encode("utf-8").decode("utf-8-sig")
    match = re.search(r'(\{.*\})', raw, re.DOTALL)
    if match:
        raw = match.group(1)
    return raw
def check_document_against_checklist(document_text: str, checklist: list[str]):
    checklist_joined = "\n".join([f"- {p}" for p in checklist])
    prompt = f"""
        ROLLE: Du er en erfaren saksbehandler innen arealplanlegging med ansvar for faglig kvalitetskontroll av planbeskrivelser.
        OPPGAVE: Vurder om planbeskrivelsen dekker hvert punkt i sjekklisten.
        REGLER:
        Sjekklisten er hierarkisk flattet ut - bruk faglig skjønn til å forstå sammenhenger mellom nummererte punkter og underpunkter.
        Et punkt er “oppfylt” hvis temaet er tilstrekkelig behandlet i dokumentet, overskriften trenger ikke matche sjekklisten ordrett, men formål og innhold må stemme overens.
        Et punkt er “ikke oppfylt” hvis det mangler helt, kun har tittel uten innhold, overskriften og innhold samsvarer ikke eller innholdet er for tynt og overfladisk.
        Vurder hvert punkt individuelt og selvstendig.
        Gi en kort begrunnelse på hva som er funnet eller hva som mangler.

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
    messages=[
        {"role": "system", "content": "Return only valid JSON. Do not add any explanation, markdown, or extra text."},
        {"role": "user", "content": prompt}
    ],
    max_completion_tokens=2000,
    #temperature=0.0
)
    raw = response.choices[0].message.content
    raw = clean_json_from_ai(raw)
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
