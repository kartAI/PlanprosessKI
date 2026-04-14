import json
from services.ai_conf import client, deployment

# Tar inn planbeskrivelse og brukerinput og formulerer forslag til et innspill.
def input_analyse(document: str, userInput: str) -> dict:
    try:
        prompt = f"""
            Du skal hjelpe en innbygger med å formulere et innspill basert på deres bekymringer.
            Du skal hjelpe en innbygger med å formulere et innspill basert på deres bekymringer.

            Du skal:
                - Formulere et innspill som er relevant for planbeskrivelsen og brukerens bekymringer.
                - Sørg for å bruke riktig fagspråklig terminologi og være presis i formuleringen.
                - Unngå å inkludere irrelevant informasjon eller gjenta det som allerede er nevnt i dokumentet
                - Returnere et fullstendig innspill som kan sendes inn direkte til kommunen uten behov for ytterligere redigering.
                - Dersom brukeren nevner irrelevante bekymringer, skal du ignorere disse og fokusere på de relevante bekymringene i innspillet.
            
            Regler: 
                - Snakk norsk bokmål
                - Snakk norsk bokmål
                - Returner KUN gyldig JSON
            
            
        PLANBESKRIVELSE:
        {document}

        BRUKERINPUT:
        {userInput}

        Gi svar som strukturert JSON med følgende format:
        {{
            "Tekst": [
                {{
                    "tittel": "Kortfattet tittel på innspillet",
                    "beskrivelse": "Detaljert beksrivelse av innspillet, inkludert relevante bekymringer"
                }}
            ]
        }}

        """
    
        response = client.chat.completions.create(
                model=deployment,
                messages=[{"role": "system", "content": prompt}],
                max_tokens=2000,
                temperature=0.5,
                top_p=1
            )
        
        return response.choices[0].message.content.strip()
    except FileNotFoundError:
        return {'error': 'Ingen dokumenter funnet'}
    except json.JSONDecodeError:
        return {'error': 'Feil ved parsing av KI-respons'}
    except Exception as e:
        return {'error': f'Uventet feil: {str(e)}'}