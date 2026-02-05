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

# ---------------------------------------------------------
# 1. Automatisk kategorisering
# ---------------------------------------------------------
def generate_categories(all_texts: list[str]):
    joined = "\n\n---\n\n".join(all_texts)

    prompt = f"""
Analyser alle høringsinnspillene og identifiser 3–7 hovedtemaer som går igjen.

Returner KUN gyldig JSON i dette formatet:

{{
  "kategorier": [
    {{
      "kategori": "...",
      "beskrivelse": "...",
      "filnavn": "..."
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
        return json.loads(raw)
    except:
        return {"error": "Ugyldig JSON", "raw": raw}


# ---------------------------------------------------------
# 2. Felles oppsummering av alle dokumenter
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
# 3. Oppsummering per kategori
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