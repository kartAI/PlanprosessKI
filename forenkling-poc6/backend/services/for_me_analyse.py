import json
from services.ai_conf import client, deployment
#Husk å bruk riktig datatype !!!!!!!!!!!!
def for_me_analyse():
    try:
        prompt = f"""
            Si noe lurt
        """

        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=1000,
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except FileNotFoundError:
        return {'error': 'Ingen dokumenter funnet'}
    except json.JSONDecodeError:
        return {'error': 'Feil ved parsing av KI-respons'}
    except Exception as e:
        return {'error': f'Uventet feil: {str(e)}'}