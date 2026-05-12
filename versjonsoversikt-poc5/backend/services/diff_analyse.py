#Analyse for endringer
#laster inn og importer biblioteker
import json
from services.ai_conf import client, deployment

#Metode for analysere endringer over alle versjoner
def analyse_all_diff(all_documents: list) -> list:
    try:
        prompt = f"""
        Du får en liste med dokumenter. Du skal:
        - Sorter dokumentene etter dato, med nyest først og eldst sist.
        - Sammenlign dokumentene og finn hva som er endret mellom hver versjon.

        REGLER:
        - Du skal ikke nevne små språklige endringer som komma, mellomrom, punktum.
        - Du skal svare på norsk bokmål med forståelige setninger.
        
        Returner KUN gyldig JSON-objekt med følgende struktur:
        {{
        "dokumentversjoner": [
            {{
            "dato": "DD-MM-YYYY",
            "filnavn": "string",
            "endringer_fra_forrige": ["string", "string"]
            }}
        ]
        }}
        DOKUMENTER:
        {all_documents}
        """
        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=1000,
            #temperature=0.1,
            #top_p=1,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content.strip())
    except FileNotFoundError:
        return {'error': 'Ingen dokumenter funnet'}
    except json.JSONDecodeError:
        return {'error': 'Feil ved parsing av KI-respons'}
    except Exception as e:
        return {'error': f'Uventet feil: {str(e)}'}

# Metode for å sammenligne to versjoner
def compare_versions(document1: str, document2: str):
    try:
        prompt = f"""
        Du få to versioner av samme dokument. Du skal:
        - Du skal sammenligne den elste mot den nyeste og finne ut hva som er endret.
        - Returner et JSON-objekt med følgende struktur (ingen markdown, kun JSON):
        
        REGLER:
        - Ikke nevn små språklige endringer som komma, mellomrom, punktum.
        - Aldri nevn endring i dato. 
        - Alt skal stå på norsk bokmål med forståelige setninger. 
        - Hvis det ikke er noen vesentlige endringer mellom to dokumenter returner: "Ingen vesentlige endringer.".
        {{
        "dokumentversjoner": [
            {{
            "endringer_fra_forrige": ["string", "string"]
            }}
        ]
        }}
        Dokument 1:
        {document1}
        Dokument 2:
        {document2}
        """
        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=3000,
            #temperature=0.1,
            #top_p=1,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content.strip())
    except FileNotFoundError:
        return {'error': 'Ingen dokumenter funnet'}
    except json.JSONDecodeError:
        return {'error': 'Feil ved parsing av KI-respons'}
    except Exception as e:
        return {'error': f'Uventet feil: {str(e)}'}