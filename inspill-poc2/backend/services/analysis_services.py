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

deployment = "gpt-4.1"

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
        max_completion_tokens=300
    )

    return response.choices[0].message.content.strip()


# ---------------------------------------------------------
# 2. Automatisk kategorisering
# ---------------------------------------------------------
def generate_categories(all_texts: list[str]):
    joined = "\n\n---\n\n".join(all_texts)

    prompt = f"""
Kategoriser hvert høringsinnspill til hvilke team som bør håndtere innholdet. Et dokument kan tilhøre flere team. Lag ikke nye team eller lange beskrivelser.
Bruk KUN disse teamene:

[
"Miljø / Klima",
"Samferdsel / Infrastruktur",
"Trafikk / Parkering",
"Bygg/plan / Arkitektur",
"Sosiale forhold / Nabolag",
"Barn / Unge",
"Universell utforming / Tilgjengelighet",
"Kultur / Historie"
]

Returner KUN gyldig JSON i dette formatet:

{{
  "kategorier": [
    {{
      "navn": "...",
      "beskrivelse": "...",
    }}
  ]
}}

Her er innspillene:
{joined}
"""

    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=500
    )

    raw = response.choices[0].message.content

    try:
        data = json.loads(raw)
        if "kategorier" not in data:
            raise ValueError("KI returnerte ikke 'kategorier'")
        return data
    except Exception as e:
        return {
            "error": "Ugyldig JSON fra KI",
            "exception": str(e),
            "raw": raw
        }

# ---------------------------------------------------------
# 3. Felles oppsummering av ALLE dokumenter
# ---------------------------------------------------------
def summarize_all_documents(summaries: list[str]) -> str:
    joined = "\n\n---\n\n".join(summaries)

    prompt = f"""
Lag en samlet oppsummering av alle høringsinnspillene.

Oppgave:
- Identifiser hovedtemaer som går igjen.
- Oppsummer hva innspillene generelt uttrykker.
- Vær kort, presis og nøytral.

Her er oppsummeringene:
{joined}
"""

    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=400
    )

    return response.choices[0].message.content.strip()


# ---------------------------------------------------------
# 4. Oppsummering per kategori
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
- Vær nøytral og konsis.

Her er innspillene:
{joined}
"""

    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=300
    )

    return response.choices[0].message.content.strip()