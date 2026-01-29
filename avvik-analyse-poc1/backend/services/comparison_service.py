import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

deployment = "gpt-4.1"

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

def compare_documents(doc1_text, doc2_text, doc3_text, doc1_name="Dokument 1", doc2_name="Dokument 2", doc3_name="Dokument 3"):
    """
    Sammenligner tre dokumenter for å sjekke om de er samstemte.
    Returnerer avvik og observasjoner.
    """
    
    prompt = f"""Du er en ekspert på dokumentsammenlikning. Sammenlign følgende tre dokumenter og identifiser:

1. **Samstemte områder**: Hva er det samme i alle tre dokumenter?
2. **Avvik**: Hvor er det ulikheter eller motstridende informasjon?
3. **Manglende informasjon**: Hva mangler i noen dokumenter?

DOKUMENT 1 ({doc1_name}):
{doc1_text[:3000]}  # Begrenset til 3000 tegn per dokument for å spare tokens

DOKUMENT 2 ({doc2_name}):
{doc2_text[:3000]}

DOKUMENT 3 ({doc3_name}):
{doc3_text[:3000]}

Gi en strukturert analyse med konkrete eksempler fra dokumentene.
"""
    
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "Du er en juridisk/teknisk dokumentanalytiker som spesialiserer seg på å identifisere avvik."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content