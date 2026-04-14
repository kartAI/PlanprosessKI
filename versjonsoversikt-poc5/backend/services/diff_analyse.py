#Analyse for endringer
#laster inn og importer biblioteker
import json
from services.ai_conf import client, deployment

#Metode for analysere endringer over alle versjoner
def analyse_all_diff(all_documents: list) -> list:
    try:
        prompt = f"""
        Du får en liste med dokumenter, der hvert element inneholder:
            - "dato": dato for versjonen
            - "filnavn": navn på dokumentet
            - "innhold": tekstinnholdet i dokumentet

        Oppgave:
            1. Sorter dokumentene etter dato (nyeste først).
            2. Sammenlign hver versjon med versjonen før den.
            3. Identifiser kun reelle, meningsbærende endringer i innholdet.

        Definisjoner:
            - "Vesentlige endringer" betyr endringer i innhold, struktur, krav, formuleringer som endrer mening, nye avsnitt, fjernede avsnitt, nye punkter, endrede punkter.
            - "Ikke-vesentlige endringer" som skal ignoreres:
                - tegnsetting (komma, punktum, mellomrom)
                - små språklige justeringer uten betydning
                - endringer i dato eller versjonsnummer

        Regler:
            - Svar alltid på norsk bokmål.
            - Svar med korte, klare setninger.
            - Returner KUN gyldig JSON med følgende struktur:

            {
            "dokumentversjoner": [
                {
                "filnavn": "string",
                "endringer_fra_forrige": ["string", "string"]
                }
            ]
            }

            Hvis ingen vesentlige endringer finnes mellom to versjoner, bruk:
            "endringer_fra_forrige": ["Ingen vesentlige endringer."]

            DOKUMENTER:
            {all_documents}
        """
        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=1000,
            temperature=0.1,
            top_p=1,
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
            max_completion_tokens=1000,
            temperature=0.1,
            top_p=1,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content.strip())
    except FileNotFoundError:
        return {'error': 'Ingen dokumenter funnet'}
    except json.JSONDecodeError:
        return {'error': 'Feil ved parsing av KI-respons'}
    except Exception as e:
        return {'error': f'Uventet feil: {str(e)}'}