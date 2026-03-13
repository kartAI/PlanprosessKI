# Laster inn og importer biblioteker
import json
from services.ai_conf import client, deployment

def analyse_meetings(all_meetings: str) -> dict:
    prompt = f"""
        Du får flere møtereferater. Du skal:
        - Hente ut alle gjeldende krav eller forslag på tvers av referatene. 
        Regler:
        - Kun inkluder den nyeste versjonen av et krav eller forslag dersom det er endret mellom møtene. 
        - Hvis et krav eller forslag er nevnt i et tidligere møtereferat, og det ikke er endret eller overstyrt i senere møtereferater, skal det beholdes som gyldig.
        - Hvis et krav eller forslag er fjernet, overstyrt eller endret i et senere møtereferat, skal kun den nyeste versjonen tas med.
        - Ignorer utdatert informasjon som er erstattet i et senere møtereferat. 
        - Inkluder seneste dato øverst i listen.
        Returner KUN gyldig JSON i dette formatet:
{{
        "oppdateringer": [
            {{
                "dato": "YYYY-MM-DD",
                "gjeldende": [
                    {{
                        "tema": "string",
                        "beskrivelse": "string"
                    }}
                ]
            }}
        ]
}}
        MØTEREFERATER:
{all_meetings}
    """
    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "system", "content": prompt}],
        max_tokens=2000,
        temperature=0.1
    )

    raw = response.choices[0].message.content

    if raw.strip().startswith("```"):
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    return json.loads(raw)  