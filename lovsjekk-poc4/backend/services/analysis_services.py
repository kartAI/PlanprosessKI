#laster inn og importer biblioteker
import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

#Koble til modellen
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

#Valg av modell
deployment = "gpt-4.1"

#Klassifisering av lovområder
def law_classification(text: str) -> str:
    prompt = f"""
    Du skal analysere en planbestemmelse og identifisere hvilke lover, forskrifter eller nasjonale retningslinjer den mest sannsynlig berører.
    
    Oppgave:
        1. Les planbestemmelsen nøye.
        2. Identifiser hvilke juridiske temaer den handler om 
        3. Basert på temaene: foreslå hvilke lover, forskrifter eller nasjonale retningslinjer som normalt regulerer slike forhold i Norge.
        4. Returner resultatet som strukturert JSON med følgende format:
{
    "temaer": ["..."],
    "relevante_lover": [
        {
            "navn": "Lov eller forskrift",
            "paragrafer_eller_kapitler": ["(hvis mulig)"],
    }
]
}
Vær tydelig, konkret og presis. Ikke finn opp lover som ikke finnes, og ikke gjett på detaljer du ikke kan begrunne.
{text} 
"""
    
    #konfig ting
    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=300
    )

    return response.choices[0].message.content.strip()




