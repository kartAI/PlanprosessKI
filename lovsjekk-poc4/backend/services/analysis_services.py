#laster inn og importer biblioteker
import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI
from typing import TypedDict

#laster inn miljøvariabler fra .env-filen
load_dotenv()

#Kobler til modellen
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)
#Valg av modell
deployment = "gpt-4.1"

# Definerer typehint for respons fra law_classification
class LawClassificationResponse(TypedDict):
    temaer: list[str] #liste over juridiske temaer
    relevante_lover: list[dict] #liste over relevante lover med navn og paragrafer

# steg 1 i pipelinen: les PDF og kjør analyse for å klassifisere planbestemmelsen
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
    #sender prompt til KI og ber om JSON-respons med spesifisert schema
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

    #parser KI-respons som JSON
    result = json.loads(response.choices[0].message.content)
    
    # Valider og konverter til liste (KI kan noen ganger returnere sets)
    if isinstance(result.get("relevante_lover"), (set, frozenset)):
        result["relevante_lover"] = list(result["relevante_lover"])
    
    if isinstance(result.get("temaer"), (set, frozenset)):
        result["temaer"] = list(result["temaer"])
    
    return result

#Bruker KI i looper for å sammenligne én del av JSON mot hele XML per iterasjon
def get_filtered_law_data(result: dict, xml_file_path: str) -> list[dict]:
    """
    Bruker KI i looper: Itererer gjennom hver lov i 'relevante_lover' (én del av JSON), 
    og sammenligner den mot hele XML for å trekke ut relevant data. Dette reduserer belastning per KI-kall.
    
    :param result: Dict fra law_classification (med 'relevante_lover')
    :param xml_file_path: Sti til XML-filen
    :return: Liste av dicts med filtrert data 
    """
    try:
        # Les hele XML-filen én gang u alle KI-kall
        with open(xml_file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        filtered_data = [] # Liste for å samle filtrert data fra alle lover
        
        # Loop gjennom hver lov i JSON (én del av JSON per iterasjon)
        for law in result.get('relevante_lover', []):
            # Eksempel på ønsket format (for å unngå format-feil)
            example = [{'navn': 'Matchende lovnavn', 'paragraf': '§X-Y', 'tekst': 'Utdraget tekst'}]
            
            # Bygg prompt for denne ene loven
            prompt = f"""
            Du skal sammenligne én lov fra JSON mot hele XML-lovtekst og trekke ut kun relevant informasjon.

            JSON-lovdata (én del):
            {json.dumps(law, ensure_ascii=False, indent=2)}

            XML-lovtekst (hele innholdet):
            {xml_content}

            XML-struktur: Loven har <paragraf id="..."> med <tittel> for navn og <ledd>/<bokstav> for tekst. Match 'paragrafer_eller_kapitler' (f.eks. §11-8) mot id-attributtet.

            Oppgave:
            1. Finn beste match for 'navn' i XML (selv om ikke identisk, f.eks. synonymer eller forkortelser).
            2. Trekk ut teksten for paragrafene eller kapitlene i 'paragrafer_eller_kapitler' (f.eks. §11-8, §11-9) ved å matche mot <paragraf id="..."> og samle tekst fra <ledd> og <bokstav>.
            3. Returner et objekt med nøkkelen "result" som inneholder listen av dicts med filtrert data: {json.dumps({"result": example}, ensure_ascii=False)}. Ignorer hvis ingen match.

            Vær presis og returner kun JSON-objekt uten ekstra tekst.
            """
            
            # Send til KI per lov med JSON-schema for strutrert respons
            response = client.chat.completions.create(
                model=deployment,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=1500,  # Juster for mindre belastning
                response_format={"type": "json_schema", "json_schema": {"name": "filtered_data", "schema": {"type": "object", "properties": {"result": {"type": "array", "items": {"type": "object", "properties": {"navn": {"type": "string"}, "paragraf": {"type": "string"}, "tekst": {"type": "string"}}, "required": ["navn", "paragraf", "tekst"]}}}, "required": ["result"]}}}
            )
            
            # Parser KI-respons og henter "result"-listen
            law_filtered_response = json.loads(response.choices[0].message.content)
            law_filtered = law_filtered_response.get("result", [])
            if isinstance(law_filtered, list):
                filtered_data.extend(law_filtered)
        
        #returnerer filtrert data eller feilmelding hvis ingen match
        return filtered_data if filtered_data else [{'error': 'Ingen matchende data funnet'}]
    
    except FileNotFoundError:
        return [{'error': 'XML-fil ikke funnet'}]
    except json.JSONDecodeError:
        return [{'error': 'Feil ved parsing av KI-respons'}]
    except Exception as e:
        return [{'error': f'Uventet feil: {str(e)}'}]
    
