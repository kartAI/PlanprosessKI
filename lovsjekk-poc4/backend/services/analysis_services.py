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
2. Identifiser hvilke juridiske temaer den handler om.
3. Basert på temaene: foreslå hvilke lover, forskrifter eller nasjonale retningslinjer som normalt regulerer slike forhold i Norge.
4. Hent kun lover fra Plan- og bygningsloven.

Vær tydelig, konkret og presis. Ikke finn opp lover som ikke finnes, og ikke gjett på detaljer du ikke kan begrunne.

PLANBESTEMMELSE:
{text}
"""
    #sender prompt til KI og ber om JSON-respons med spesifisert schema
    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=700,
        temperature=0.1,
        top_p=1,
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
        # Les hele XML-filen én gang før alle KI-kall
        with open(xml_file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        filtered_data = [] # Liste for å samle filtrert data fra alle lover
        
        # Loop gjennom hver lov i JSON (én del av JSON per iterasjon)
        for law in result.get('relevante_lover', []):
            # Bygg prompt for denne ene loven
            prompt = f"""
                Du skal sammenligne én lov fra JSON mot hele XML-lovtekst og trekke ut kun relevant informasjon.

                Krav:
                    - Bruk kun informasjon som finnes i XML.
                    - Hvis ingen treff: returner tom "result"-liste.
                    - Hver bokstav/punkt skal være eget objekt.
                    - Hvis bokstav/punkt finnes: prioriter relevante bokstav/punkt + relevante ledd.
                    - Hvis bokstav/punkt ikke finnes: returner relevante ledd.
                    - Ikke gjenta tekst eller lag synonymer.
                    - "begrunnelse" skal være kort: maks 1 setning og forklare hvorfor dette er relevant i forhold til innhold.
                    - Kun nevn det som faktisk finnes i XML, ikke gjetninger.
                    - Skriv ut bokstav og punkt hvis det finnes, ellers bare ledd.
                    - IKKE gjenta informasjon som allerede er nevnt.
                    - Skriv hvilken paragraf punkt og bokstav tilhører i "bokstav_eller_punkt" for å unngå forvirring.

                JSON-lovdata (én del):
                {json.dumps(law, ensure_ascii=False, indent=2)}

                XML-lovtekst (hele innholdet):
                {xml_content}

                Returner KUN gyldig JSON med format:
                    {{
                    "result": [
                        {{
                        "navn": "Paragrafens navn",
                        "bokstav_eller_punkt": "a" eller "1" (identifikator),
                        "tekst": "Teksten fra bokstaven eller punktet",
                        "ledd": "Tilhørende leddtekst (hvis relevant)",
                        "begrunnelse": "Kort forklaring på hvorfor dette er relevant og hvorfor annet er ignorert"
                        }}
                    ]
                    }}
                """
            
            # Send til KI per lov med JSON-schema for strukturert respons
            response = client.chat.completions.create(
                model=deployment,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=1500, 
                temperature=0.1,
                top_p=1,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "filtered_data", 
                        "schema": {
                            "type": "object", 
                            "properties": {
                                "result": {
                                    "type": "array", 
                                    "items": {
                                        "type": "object", 
                                        "properties": {
                                            "navn": {"type": "string"},
                                            "bokstav_eller_punkt": {"type": "string"},
                                            "tekst": {"type": "string"},
                                            "ledd": {"type": "string"},
                                            "begrunnelse": {"type": "string"}
                                        }, 
                                        "required": ["navn","bokstav_eller_punkt", "tekst", "ledd", "begrunnelse"]
                                    }
                                }
                            }, 
                            "required": ["result"]
                        }
                    }
                }
            )
            
            # Parser KI-respons og henter "result"-listen
            law_filtered_response = json.loads(response.choices[0].message.content)
            law_filtered = law_filtered_response.get("result", [])
            if isinstance(law_filtered, list):
                filtered_data.extend(law_filtered)
        
        # Returnerer filtrert data eller feilmelding hvis ingen match
        return filtered_data if filtered_data else [{'error': 'Ingen matchende data funnet'}]
    
    except FileNotFoundError:
        return [{'error': 'XML-fil ikke funnet'}]
    except json.JSONDecodeError:
        return [{'error': 'Feil ved parsing av KI-respons'}]
    except Exception as e:
        return [{'error': f'Uventet feil: {str(e)}'}]
    

#funskjon for å sjekke om bestemmelsen strider imot lovverket
def analyse_law_conflict(text: str, filtered_data: list[dict]) -> dict:
    try:
        analysed_data = []  # Samler alle vurderinger

        # filtered_data kommer inn som liste fra get_filtered_law_data
        if not isinstance(filtered_data, list):
            return {"result": [{"error": "Ugyldig input til analyse_law_conflict"}]}

        # Hvis forrige steg allerede ga en feilmelding, send den videre
        upstream_errors = [
            item for item in filtered_data
            if isinstance(item, dict) and item.get("error")
        ]
        if upstream_errors:
            return {"result": upstream_errors}

        # Loop direkte over listen (ikke .get på list)
        for law in filtered_data:
            prompt = f"""
                Du skal analysere en planbestemmelse og vurdere om den strider imot lovverket basert på filtrert data fra XML.

                Instruks:
                - Sammenlign planbestemmelsen med hvert lovpunkt.
                - Sett vurdering: "strider", "delvis_strider", "ikke_strider" eller "uklar".
                - Sett konfliktgrad: "lav", "middels" eller "hoy".
                - planutdrag og lovutdrag skal være korte sitater (1–3 linjer).
                - Begrunnelse maks 2 setninger.
                - Bruk kun informasjon fra teksten og lovpunktet. Ikke anta noe.

                Planbestemmelse:
                {text}
                
                Filtrerte lover (én del):
                {json.dumps(law, ensure_ascii=False, indent=2)}

                Returner KUN gyldig JSON med format:
                        {{
                        "result": [
                            {{
                            "navn": "Paragrafens navn",
                            "bokstav_eller_punkt": "a" eller "1" (identifikator),
                            "tekst": "Teksten fra bokstaven eller punktet",
                            "ledd": "Tilhørende leddtekst (hvis relevant)",
                            "begrunnelse": "Kort forklaring på hvorfor dette er relevant og hvorfor annet er ignorert"
                            }}
                        ]
                        }}
            """

            response = client.chat.completions.create(
                    model=deployment,
                    messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=2000, 
                    temperature=0.3,
                    top_p=1,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "law_conflict_analysis",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "result": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "navn": {"type": "string"},
                                                "bokstav_eller_punkt": {"type": "string"},
                                                "vurdering": {
                                                    "type": "string",
                                                    "enum": ["strider", "delvis_strider", "ikke_strider", "uklar"]
                                                },
                                                "konfliktgrad": {
                                                    "type": "string",
                                                    "enum": ["lav", "middels", "hoy"]
                                                },
                                                "planutdrag": {"type": "string"},
                                                "lovutdrag": {"type": "string"},
                                                "begrunnelse": {"type": "string"}
                                            },
                                            "required": [
                                                "navn",
                                                "bokstav_eller_punkt",
                                                "vurdering",
                                                "konfliktgrad",
                                                "planutdrag",
                                                "lovutdrag",
                                                "begrunnelse"
                                            ]
                                        }
                                    },
                                    "oppsummering": {
                                        "type": "object",
                                        "properties": {
                                            "totalt_vurdert": {"type": "integer"},
                                            "strider": {"type": "integer"},
                                            "delvis_strider": {"type": "integer"},
                                            "ikke_strider": {"type": "integer"}
                                        },
                                        "required": ["totalt_vurdert", "strider", "delvis_strider", "ikke_strider"]
                                    }
                                },
                                "required": ["result", "oppsummering"]
                            }
                        }
                    }
                )
                # Parser KI-respons og henter "result"-listen
            analyse_response = json.loads(response.choices[0].message.content)
            result_items = analyse_response.get("result", [])
            if isinstance(result_items, list):
                analysed_data.extend(result_items)
                    
        # Returnerer filtrert data eller feilmelding hvis ingen match
        return {
            "result": analysed_data if analysed_data else [{"error": "Ingen matchende data funnet i analysen"}]
        }

        
    except json.JSONDecodeError:
        return {"result": [{"error": "Feil ved parsing av KI-respons"}]}
    except Exception as e:
        return {"result": [{"error": f"Uventet feil: {str(e)}"}]}