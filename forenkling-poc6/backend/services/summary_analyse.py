import json
from services.ai_conf import client, deployment

#husk å bruk riktig returtype!!!!!!! (dict)
def summary_analyse(summary: str) -> dict:
    return