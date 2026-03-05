#laster inn og importer biblioteker
import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI
from typing import TypedDict

load_dotenv()

#Koble til modellen
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

#Valg av modell
deployment = "gpt-4.1"

# Definer strukturen
class LawClassificationResponse(TypedDict):
    temaer: list[str]
    relevante_lover: list[dict]

def law_classification(text: str) -> dict:
    prompt = f"""
Du skal analysere en planbestemmelse og identifisere hvilke lover, forskrifter eller nasjonale retningslinjer den mest sannsynlig berører.

Oppgave:
1. Les planbestemmelsen nøye.
2. Identifiser hvilke juridiske temaer den handler om. (for eksempel bygging, arealbruk, miljø, naturinngrep, støy, kulturminner, 
    universell utforming, trafikksikkerhet, tekniske krav, sikkerhet osv.).
3. Basert på temaene: foreslå hvilke lover, forskrifter eller nasjonale retningslinjer som normalt regulerer slike forhold i Norge.

Vær tydelig, konkret og presis. Ikke finn opp lover som ikke finnes, og ikke gjett på detaljer du ikke kan begrunne.

PLANBESTEMMELSE:
{text}
"""
    
    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=1000,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "law_classification",
                "schema": {
                    "type": "object",
                    "properties": {
                        "temaer": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "relevante_lover": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "navn": {"type": "string"},
                                    "paragrafer_eller_kapitler": {"type": "string"}
                                },
                                "required": ["navn", "paragrafer_eller_kapitler"]
                            }
                        }
                    },
                    "required": ["temaer", "relevante_lover"]
                }
            }
        }
    )

    result = json.loads(response.choices[0].message.content)
    
    # Valider og konverter til liste (sikrer at det er liste, ikke set)
    if isinstance(result.get("relevante_lover"), (set, frozenset)):
        result["relevante_lover"] = list(result["relevante_lover"])
    
    if isinstance(result.get("temaer"), (set, frozenset)):
        result["temaer"] = list(result["temaer"])
    
    return result


