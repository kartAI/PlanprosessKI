# Bachelorprosjekt - PlanprosessKI

Repo for Gruppe 7 - 2026

## Hovedproblemstilling

Planprosessen er i dag preget av store dokumentmengder, tidkrevende arbeidsflyt og mange involverte aktører. Kommunene etterspør konkrete eksempler på hvordan kunstig intelligens (KI) kan gi praktisk nytteverdi i planarbeid. Målet med prosjektet var derfor å utforske disse mulighetene ved å utvikle flere proof-of-concepts (POC) som demonstrerte konkrete anvendelsesområder.

Problemstillingen for prosjektet var: Hvordan kan kunstig intelligens brukes til å støtte konkrete deler av planprosessen, og hvilken nytteverdi opplever fagpersoner og innbyggere ved bruk av KI-verktøy? 

### Prosjektstruktur

```
PlanprosessKI/
├── README.md
├── LICENSE
├── avvik-analyse-poc1/
│   ├── requirements.txt
│   ├── backend/
│   │   ├── file.py
│   │   ├── extract_info.py
│   │   ├── test_pdf.py
│   │   ├── json/
│   │   │   └── plankart.json
│   │   ├── services/
│   │   │   ├── analysis_service.py
│   │   │   └── comparison_service.py
│   │   ├── test/
│   │   │   └── test_gpt.py
│   │   └── uploads/
│   └── frontend/
│       ├── avvik.html
│       ├── index.html
│       └── js/
│           ├── avvik.js
│           └── script.js
├── inspill-poc2/
│   ├── requirements.txt
│   ├── backend/
│   │   ├── app.py
│   │   ├── read_pdf.py
│   │   ├── services/
│   │   │   └── analysis_services.py
│   │   ├── test/
│   │   │   └── test_auto_categorize.py
│   │   └── uploads/
│   └── frontend/
│       ├── index.html
│       ├── oppsummering.html
│       └── js/
│           └── script.js
├── sjekkliste-poc3/
│   ├── requirements.txt
│   ├── backend/
│   │   ├── app.py
│   │   ├── read_pdf.py
│   │   ├── test_connection.py
│   │   ├── services/
│   │   │   └── analysis_service.py
│   │   ├── sjekklister/
│   │   └── uploads/
│   └── frontend/
│       ├── index.html
│       ├── sjekkliste.html
│       └── js/
│           └── script.js
├── lovsjekk-poc4/
│   ├── requirements.txt
│   ├── backend/
│   │   ├── app.py
│   │   ├── lovverk.xml
│   │   ├── read_pdf.py
│   │   ├── services/
│   │   │   └── analysis_services.py
│   │   └── uploads/
│   └── frontend/
│       ├── index.html
│       ├── lovAnalyse.html
│       └── js/
│           └── script.js
├── versjonsoversikt-poc5/
│   ├── requirements.txt
│   ├── backend/
│   │   ├── app.py
│   │   ├── meetings/
│   │   ├── services/
│   │   │   ├── ai_conf.py
│   │   │   ├── curr_analyse.py
│   │   │   ├── diff_analyse.py
│   │   │   └── pdf_reader.py
│   │   └── uploads/
│   └── frontend/
│       ├── endring.html
│       ├── gjelder.html
│       ├── header.html
│       ├── index.html
│       ├── sammenligning.html
│       └── js/
│           ├── current.js
│           ├── endring.js
│           ├── index.js
│           ├── sammenligning.js
│           └── script.js
├── forenkling-poc6/
│   ├── requirements.txt
│   ├── backend/
│   │   ├── app.py
│   │   ├── properties.json
│   │   ├── services/
│   │   │   ├── ai_conf.py
│   │   │   ├── for_me_analyse.py
│   │   │   ├── input_analyse.py
│   │   │   ├── summary_analyse.py
│   │   │   └── tools.py
│   │   └── uploads/
│   └── frontend/
│       ├── for_meg.html
│       ├── header.html
│       ├── index.html
│       ├── innspill.html
│       ├── oppsummering.html
│       └── js/
│           ├── for_meg.js
│           ├── index.js
│           ├── innspill.js
│           ├── oppsummering.js
│           └── script.js
└── css/
    └── style.css
```

## Proof of Concept 1 - Sjekk avvik mellom dokumenter i et planforslag
### Bakgrunn
Et planforslag består av flere dokumenter, som plankart, planbestemmelser og planbeskrivelse. Det kan være tidkrevende å kontrollere at disse stemmer overens og ikke inneholder avvik eller motstridende informasjon.

### Konsept
Utforsker hvordan KI kan brukes til å lese gjennom alle dokumentene i et planforslag samlet, og identifisere avvik, mangler eller potensielle konflikter mellom dem.

### Problemstilling 
_Hvordan kan KI brukes til å identifisere relevante avvik mellom plandokumenter på en presis og forståelig måte for fagpersoner?_

## Proof of Concept 2 - Oppsummering og kategorisering av høringsinnspill
### Bakgrunn
Det kan komme mange høringsinnspill og merknader i løpet av en planprosess, som ofte er tidkrevende og uoversiktlige å lese og oppsummere. Det kan være vanskelig å rask få en oversikt over hovedtemaene og hva som går igjen i innspillene.

### Konsept
Konseptet går ut på å utforske hvordan KI kan brukes til å oppsummere, strukturere og kategorisere høringsinnspill, slik at det blir lettere å se de viktigste temaene og mønstrene.

### Problemstilling
_Hvordan kan KI brukes til å oppsummere innspill presist og kategorisere dem på en måte som gir saksbehandlere et raskt og nyttig overblikk?_

## Proof of Concept 3 - Sjekkliste for planbeskrivelse
### Bakgrunn
Planbeskrivelser må ofte oppfylle en rekke krav og punkter fra sjekklister og maler. Det kan være krevende og tidkrevende å sikre at alle nødvendige punkter er inkludert og tilstrekkelig besvart.

### Konsept
Konseptet går ut på å utforske hvordan KI kan brukes til å sammenligne planbeskrivelsen med en gitt sjekkliste eller mal, og automatisk identifisere manglende eller ufullstendige punkter.

### Problemstilling
_Hvordan kan KI brukes til å verifisere om kravene i sjekklisten er inkludert og eventuelt oppfylt i planbeskrivelsen?_

## Proof of Concept 4 - Lovsjekk av planbestemmelser
### Bakgrunn
Saksbehandler må gå gjennom planbestemmelsen og sjekke om den er i henhold til lovverket. Det kan være vanskelig og tidkrevende å sjekke hele planbestemmelsen opp mot lovverket.

### Konsept
Konseptet går ut på å utforske hvordan KI kan sjekke en planbestemmelse opp mot lovverket, henvise til relevante lover og avgjøre om bestemmelsen har hjemmel i forhold til lovverket.

### Problemstilling 
_Hvordan kan KI brukes til å vurdere om en planbestemmelse er i tråd med lovverket og identifisere eventuelle avvik på en presis og forståelig måte?_

## Proof of Concept 5 - Versjonsoversikt over planbeskrivelse
### Bakgrunn
Det kommer nye dokumenter og versjoner gjennom hele prosessen, og det er vanskelig å holde styr på endringer som blir gjort underveis i planprosessen.

### Konsept
Konseptet går ut på å utforske hvordan KI kan brukes til å lage en versjonsoversikt for endringene som skjer i plandokumenter fortløpende underveis i planprosessen.

### Problemstilling
_Hvordan kan KI brukes til å identifisere og oppsummere endringer mellom ulike versjoner av plandokumenter på en måte som gir saksbehandlere en rask og informativ oversikt?_

## Proof of Concept 6 - Forenkling av planbeskrivelse for innbyggere
### Bakgrunn
Planmateriale er omfattende og er preget av tungt og faglig språk som kan være vanskelig for innbyggere å tolke.

### Konsept
Konseptet går ut på å utforske hvordan KI kan brukes til å oppsummere virkningene av et planforslag for innbyggere uten planfaglig kompetanse.

### Problemstilling
_Hvordan kan KI brukes til å oppsummere et planforslag på en måte som gjør det enklere for innbyggere å forstå hvordan forslaget påvirker deres eiendom, nærmiljø og dagligliv?_ 

## Setup and run (Windows, PowerShell)

1. Lag virtuelt miljø

For Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

For Mac

```powershell
python -m venv .venv
source .venv/bin/activate
```

2. Installer avhengigheter:

```powershell
pip install -r requirements.txt
```

3. Kjør backend (fra `backend` mappe):

POC 1
```powershell
python file.py
```

POC 2, 3, 4, 5 og 6
```powershell
python app.py
```

