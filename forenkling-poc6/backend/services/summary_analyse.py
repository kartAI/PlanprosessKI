import json
from services.ai_conf import client, deployment

#husk å bruk riktig returtype!!!!!!! (dict)
def summary_analyse(document: str) -> dict:
    try:
        prompt = f"""
        Du får en planbeskrivelse. Du skal:
        - Vise hvert punkt i en planbeskrivelsen.
        - Oppsummere alle underpunktene til hvert punkt.
        
        Regler:
        - Du skal svare på norsk bokmål med forståelige setninger.
        - Hold svaret kort og presist.
        - Planfaglige begreper du tar med i oppsummeringen skal umiddelbart forklares på en enkel måte i en parentes. 

        Returner KUN gyldig JSON-objekt med følgende struktur:
        {{
            "punkt": [
                {{
                "tittel": "string",
                "underpunkter": [
                    {{
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
                max_completion_tokens=4000,
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