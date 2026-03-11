#Analyse for Gjeldene
#laster inn og importer biblioteker
import json
from services.ai_conf import client, deployment


#metode for å finne hva som gjelder nå
def analyse_current_agreement():
    return