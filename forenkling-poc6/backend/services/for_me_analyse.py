import json
from services.ai_conf import client, deployment

def for_me_analyse(address_data: dict, document: str) -> str:
    try:
        prompt = f"""
        Du er en assistent som hjelper innbyggere å forstå kommunale plandokumenter.
        
            - Du skal bruke koordinatene som står i planbeskrivelsen og koordinatene for å finne avstanden mellom planforslaget og adressen.
            - Du skal basert på avstand avgjøre hvordan eiendomen blir påvirket av planforslaget (for eksempel, skygge, støy, trafikk osv.)
            - Du skal dele inn i temaer
            - Du skal returnere en punktliste der hvert punkt er en kort forklaring på hvordan eiendommen påvirkes av planforslaget
            - Bruk enkelt språk, dersom det er vanskelige begreper, forklar dem

            Regler: 
            - Hvis det ikke er nok informasjon i dokumentet for å gi en vurdering, skal du si at det ikke er nok informasjon.
            - Hvis det er informasjon i dokumentet som indikerer at eiendommen ikke blir påvirket, skal du si at eiendommen ikke blir påvirket.
            - Returner kun gyldig JSON
            - Snakk norsk bokmål
        
        
        KOORDINATER:
        Lat: {address_data.get('lat')}, Lon: {address_data.get('lon')}

        PLANFORSLAG:
        {document}

        Basert på planedokumentene, analyser og identifiser hva som gjelder for adressen "{address_data.get('address')}".

        Gi svar som strukturert JSON med følgende format:
        {{
            "punkter": [
                {{
                    "tittel": "Kortfattet tittel på regelverket/plankravet",
                    "beskrivelse": "Kort forklaring av hva det betyr for denne adressen"
                }}
            ]
        }}

        """

        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=2000,
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except FileNotFoundError:
        return {'error': 'Ingen dokumenter funnet'}
    except json.JSONDecodeError:
        return {'error': 'Feil ved parsing av KI-respons'}
    except Exception as e:
        return {'error': f'Uventet feil: {str(e)}'}