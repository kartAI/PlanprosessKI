import json
from services.ai_conf import client, deployment

#husk å bruk riktig returtype!!!!!!! (dict)
def summary_analyse(document: str) -> dict:
    try:
        prompt = f"""
        Du er en faglig assistent som hjelper vanlige folk å forstå offentlige plandokumenter. 

        Du får en planbeskrivelse og skal lage en strukturert oppsumering. 
        Du skal:
        - Gå gjennom hvert hovedkapittel i planbeskrivelsen i den rekkefølgen de står i.
        - Oppsummere alle underkapittel til hvert hovedpunkt med korte og presise setninger.
        - Underkapittel som er lange kan ha en lengre oppsummering.
        
        Instruksjoner:
        For hvert hovedkapittel:
        - Sett "tittel" til kapittelnummer og navn (f.eks. "2. Planområdet").
        - Lag ett "underpunkt" per underkapittel og navn (2.1, 2.2) 
        - Hvis et hovedkapittel ikke har underkapitler, lag ett underpunkt som oppsummerer hele kapitlet.
        
        Regler:
        - Du skal svare på norsk bokmål med forståelige, fulle setninger.
        - Hold svaret kort og presist.
        - Planfaglige begreper du tar med i oppsummeringen skal umiddelbart forklares på en enkel måte i en parentes. 
        - Ikke legg til informasjon som ikke finnes i plandokumentet. 
        - Hvis et punkt mangler informasjon, skriv: "Ikke omtalt i dokumentet". 
        
        Returner KUN gyldig JSON-objekt med følgende struktur:
        {{
            "punkt": [
                {{
                    "tittel": "string",
                    "underpunkter": [
                        {{
                            "tittel": "string",
                            "beskrivelse": "..."
                        }}
                    ]
                }}
            ]
        }}
        PLANBESKRIVELSE:
        {document}
    """
        response = client.chat.completions.create(
                model=deployment,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=6000,
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