#laster inn og importer biblioteker
import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI
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

# Steg 1: identifiser relevante lover fra Plan- og bygningsloven (input til get_filtered_law_data)
def law_classification(text: str) -> dict:
    prompt = f"""
Identifiser juridiske temaer i planbestemmelsen og velg fra Plan- og bygningsloven hvilke paragrafer som normalt regulerer slike forhold.
Kun lover fra Plan- og bygningsloven. Finn ikke opp lover som ikke finnes.

PLANBESTEMMELSE:
{text}
"""
    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=600,
        temperature=0.1,
        top_p=1,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "law_classification",
                "schema": {
                    "type": "object",
                    "properties": {
                        "temaer": {"type": "array", "items": {"type": "string"}},
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
    if isinstance(result.get("relevante_lover"), (set, frozenset)):
        result["relevante_lover"] = list(result["relevante_lover"])
    if isinstance(result.get("temaer"), (set, frozenset)):
        result["temaer"] = list(result["temaer"])
    return result

# Steg 2: trekk ut relevante lovtekster fra XML (input til analyse_law_conflict)
def get_filtered_law_data(result: dict, xml_file_path: str) -> list[dict]:
    try:
        with open(xml_file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        filtered_data = []
        for law in result.get('relevante_lover', []):
            prompt = f"""Finn i XML bokstavene/punktene som matcher JSON-lovdata. 
            For hvert treff: navn, bokstav_eller_punkt, tekst, ledd, begrunnelse (kort hvorfor relevant). 
            Bruk kun innhold fra XML. 
            Hvis ingen treff: returner tom "result"-liste. 
            Hver bokstav/punkt = eget objekt.

JSON-lovdata:
{json.dumps(law, ensure_ascii=False, indent=2)}

XML-lovtekst:
{xml_content}

Returner JSON med "result"-array av objekt med navn, bokstav_eller_punkt, tekst, ledd, begrunnelse."""
            response = client.chat.completions.create(
                model=deployment,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=1200,
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
                                        "required": ["navn", "bokstav_eller_punkt", "tekst", "ledd", "begrunnelse"]
                                    }
                                }
                            }, 
                            "required": ["result"]
                        }
                    }
                }
            )
            
            law_filtered_response = json.loads(response.choices[0].message.content)
            law_filtered = law_filtered_response.get("result", [])
            if isinstance(law_filtered, list):
                filtered_data.extend(law_filtered)

        return filtered_data if filtered_data else [{'error': 'Ingen matchende data funnet'}]
    
    except FileNotFoundError:
        return [{'error': 'XML-fil ikke funnet'}]
    except json.JSONDecodeError:
        return [{'error': 'Feil ved parsing av KI-respons'}]
    except Exception as e:
        return [{'error': f'Uventet feil: {str(e)}'}]
    

# Steg 3: vurder bestemmelsen deler mot lovverket (det som vises i frontend)
def analyse_law_conflict(text: str, filtered_data: list[dict]) -> dict:
    try:
        if not isinstance(filtered_data, list):
            return {"result": [{"error": "Ugyldig input til analyse_law_conflict"}]}

        upstream_errors = [
            item for item in filtered_data
            if isinstance(item, dict) and item.get("error")
        ]
        if upstream_errors:
            return {"result": upstream_errors}

        # Én felles kall: hele bestemmelsen + alle relevante lovpunkter
        laws_json = json.dumps(filtered_data, ensure_ascii=False, indent=2)
        prompt = f"""
            Du skal analysere og tolke planbestemmelsen og lovverksteksten, og vurdere om planens deler strider mot loven.

            Oppgave:
            1. Tolke planbestemmelsen: Identifiser meningsfulle deler/punkter/avsnitt (bestemmelser, krav, temaer). Du kan tolke hva planen faktisk krever, tillater eller begrenser – også implisitt.
            2. Tolke lovene: Bruk lovteksten og eventuelle tolkninger som er gitt. Vurder hva hver lovbestemmelse krever, tillater eller begrenser i praksis.

            3. Vurdering per plan-del:
            - "strider": Plan-delen er i klar konflikt med loven (tillater noe loven forbyr, svekker et krav, eller bryter med lovens intensjon).
            - "delvis strider": Plan-delen har både elementer som er i konflikt og elementer som er i samsvar/strengere, eller deler av teksten er uklare mens andre viser konflikt.
            - "ikke strider": Plan-delen er forenlig med loven eller strengere enn loven, uten å svekke krav.
            - "uklar": Tekstene er for vage, eller det er for lite overlapp til å vurdere konflikt.

            Beslutningsregler:
            - Hvis det finnes én tydelig konflikt uten kompenserende innstramming → "strider".
            - Hvis det finnes både konflikt og samsvar/strengere krav, eller konflikt + uklarhet → "delvis strider".
            - Hvis ingen deler svekker lovens krav → "ikke strider".
            - Hvis du ikke kan avgjøre → "uklar".

            4. I "begrunnelse": forklar vurderingen (2–4 setninger). Ved strider eller delvis strider: hvilken lov og hvorfor. Ved ikke-strider: kort hvorfor den er forenlig.

            5. Hvis plan-del strider eller delvis strider: fyll ut "motstridende_lov" med paragraf/lovpunkt (f.eks. "§ 11-8 bokstav a") og kort lovtekst. Ellers tom streng.

            6. Når du fyller ut "lovtekst":
            - Finn riktig lovpunkt i "Relevante lovpunkter".
            - Kopier relevant tekst direkte fra lovpunktet (1–3 linjer).
            - Ta med både tekst, ledd og bokstav/punkt hvis tilgjengelig.
            - Dette gjelder både "strider" og "delvis strider".

            Planbestemmelse:
            {text}

            Relevante lovpunkter fra lovverket:
            {laws_json}

            Returner KUN gyldig JSON med dette formatet:
            {{
            "result": [
                {{
                "plan_del": "nummer eller tittel og kort sitat eller beskrivelse av dette punktet i planen",
                "vurdering": "strider" eller "delvis strider" eller "ikke strider" eller "uklar",
                "motstridende_lov": "F.eks. § 11-8 bokstav a. Skal fylles ut ved strider og delvis strider. Tom streng kun ved ikke strider eller uklar.",
                "lovtekst": "Kort utdrag av lovteksten som er i konflikt. Skal fylles ut ved strider og delvis strider. Tom streng ved ikke strider eller uklar.",
                "begrunnelse": "Begrunnelse for vurderingen; ved konflikt hvilken lov og hvorfor. 2–4 setninger er greit."
                }}
            ]
            }}
        """

        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=4000,
            temperature=0.25,
            top_p=1,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "plan_conflict_analysis",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "result": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "plan_del": {"type": "string"},
                                        "vurdering": {
                                            "type": "string",
                                            "enum": ["strider", "ikke strider", "delvis strider", "uklar"]
                                        },
                                        "motstridende_lov": {
                                            "type": "string",
                                            "description": "Obligatorisk ved 'strider' og 'delvis strider'. Tom streng ellers."
                                        },
                                        "lovtekst": {
                                            "type": "string",
                                            "description": "Kort utdrag av lovteksten som er i konflikt. Skal fylles ut ved strider og delvis strider."
                                        },
                                        "begrunnelse": {"type": "string"}
                                    },
                                    "required": ["plan_del", "vurdering", "lovtekst", "begrunnelse"]
                                }
                            }
                        },
                        "required": ["result"]
                    }
                }
            }
        )

        analyse_response = json.loads(response.choices[0].message.content)
        result_items = analyse_response.get("result", [])
        if not isinstance(result_items, list):
            result_items = []

        return {
            "result": result_items if result_items else [{"error": "Ingen deler kunne vurderes i planbestemmelsen"}]
        }

    except json.JSONDecodeError:
        return {"result": [{"error": "Feil ved parsing av KI-respons"}]}
    except Exception as e:
        return {"result": [{"error": f"Uventet feil: {str(e)}"}]}
