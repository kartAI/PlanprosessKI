#Analyse for Gjeldene
#laster inn og importer biblioteker
import json
from services.ai_conf import client, deployment
import os
import re
from datetime import datetime

def analyse_meetings(all_meetings: str) -> str:
    prompt = (
        "Du får flere møtereferater. Hent ut alle gjeldende krav og forslag på tvers av referatene. "
        "Kun inkluder den nyeste versjonen av et punkt dersom det er endret mellom møtene. "
        "Behold punkter fra tidligere møter som fortsatt er gyldige og ikke er overstyrt. "
        "Ignorer utdatert informasjon som er erstattet i et senere møtereferat. "
        "Returner en strukturert punktliste over alle gjeldende krav og forslag, KUN som gyldig JSON.\n\n"
        "MØTEREFERATER:\n"
        f"{all_meetings}"
    )

    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "system", "content": prompt}],
        max_tokens=2000,
        temperature=0.1
    )
    return response.choices[0].message.content

# Eksempel på bruk:
# result = analyse_meetings_with_ai('meetings/')
# print(result)  # Kan sendes til frontend