import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

deployment = "gpt-5.1-chat"

# 1. Oppsummer ett dokument
# ---------------------------------------------------------
def summarize_single_document(text: str) -> str:
    prompt = f"""
Oppsummer følgende høringsinnspill kort, presist og nøytralt:

{text}
"""

    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=1000,
        seed=42
    )

    return response.choices[0].message.content.strip()

# ---------------------------------------------------------
# 2. Generer kategorier fra innhold
# ---------------------------------------------------------
def generate_categories(summaries: list[str]) -> list[str]:
    """Returnerer en liste med kategorinavn basert på innholdet."""
    joined = "\n\n---\n\n".join(summaries)

    prompt = f"""
Du får sammendrag av flere høringsinnspill.
Lag en liste med tematiske kategorier som dekker innholdet i alle innspillene godt.

Regler:
- Kategorinavnene skal være korte (2–5 ord)
- Det skal ikke være overlapp mellom kategorier
- Dekk alle hovedtemaer i innspillene
- Ikke lag flere kategorier enn nødvendig
- Ikke lag kategorier for noe som ikke har et innspill

Returner KUN gyldig JSON:
{{"kategorier": ["Kategori A", "Kategori B", "Kategori C"]}}

Innspill:
{joined}
"""

    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=1000,
        seed=42
    )

    raw = response.choices[0].message.content.strip()
    data = json.loads(raw)
    return data["kategorier"]

# ---------------------------------------------------------
# 3. Klassifiser hvert dokument inn i kategoriene
# ---------------------------------------------------------
def classify_documents(documents: list[dict], kategorier: list[str]) -> dict:
    """Returnerer {filnavn: [kategori1, ...]}"""
    
    doc_list = "\n\n".join([
        f"Dokument: {doc['filename']}\n{doc['summary']}"
        for doc in documents
    ])
    kategori_liste = "\n".join(f"- {k}" for k in kategorier)

    prompt = f"""
Klassifiser hvert dokument til én eller flere av disse kategoriene:
{kategori_liste}

Regler:
- Bruk KUN kategoriene listet ovenfor, ord for ord
- Et dokument kan tilhøre flere kategorier

Returner KUN gyldig JSON:
{{
    "filnavn.pdf": ["Kategori A", "Kategori B"],
    "fil.pdf": ["Kategori C"]
}}

Dokumenter:
{doc_list}
"""

    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=1000,
        seed=42
    )

    raw = response.choices[0].message.content.strip()
    return json.loads(raw)

# ---------------------------------------------------------
# 4. Felles oppsummering av ALLE dokumenter
# ---------------------------------------------------------
def summarize_all_documents(summaries: list[str]) -> str:
    joined = "\n\n---\n\n".join(summaries)

    prompt = f"""
Lag en samlet oppsummering av alle høringsinnspillene.

Oppgave:
- Identifiser hovedtemaer som går igjen.
- Oppsummer hva innspillene generelt uttrykker.
- Vær kort, presis og nøytral. 
- Gå rett på oppsummeringen

Formatering:
- Skill hvert tema eller poeng med linjeskift.

Her er oppsummeringene:
{joined}
"""

    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=1500,
        seed=42
    )

    return response.choices[0].message.content.strip()

# ---------------------------------------------------------
# 5. Oppsummering per kategori
# ---------------------------------------------------------
def summarize_category(name: str, texts: list[str]) -> str:
    if not texts:
        return "Ingen dokumenter i denne kategorien."

    joined = "\n\n---\n\n".join(texts)

    prompt = f"""
Lag en kort og presis oppsummering av høringsinnspill som handler om kategorien: {name}.

Oppgave:
- Oppsummer hva innspillene sier om denne kategorien.
- Identifiser hovedbekymringer, forslag eller temaer.
- Vær kort, nøytral og konsis.
- Gå rett på oppsummeringen

Formatering:
- Skill hvert tema eller poeng med linjeskift.

Her er innspillene:
{joined}
"""

    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=1000,
        seed=42
    )

    return response.choices[0].message.content.strip()