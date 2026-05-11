# Bachelorprosjekt - PlanprosessKI

Repo for Gruppe 7 - 2026

## Hovedproblemstilling

Problemstillingen for prosjektet var: Hvordan kan kunstig intelligens brukes til å støtte konkrete deler av planprosessen, og hvilken nytteverdi opplever fagpersoner og innbyggere ved bruk av KI-verktøy? 

### Prosjektstruktur

KOMMER

## Proof of Concept 1 - Sjekk avvik mellom dokumenter i et planforslag
### Bakgrunn
Et planforslag består av flere dokumenter, som plankart, planbestemmelser og planbeskrivelse. Det kan være tidkrevende å kontrollere at disse stemmer overens og ikke inneholder avvik eller motstridende informasjon.

### Konsept
Utforsker hvordan KI kan brukes til å lese gjennom alle dokumentene i et planforslag samlet, og identifisere avvik, mangler eller potensielle konflikter mellom dem.

### Problemstilling 
_Hvordan kan KI brukes til å identifisere relevante avvik mellom plandokumenter på en presis og forståelig måte for fagpersoner?_

## Proof of Concept 2 - Oppsummering av høringsinnspill
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

## Proof of Concept 4 - Lovsjekk
### Bakgrunn
Saksbehandler må gå gjennom planbestemmelsen og sjekke om den er i henhold til lovverket. Det kan være vanskelig og tidkrevende å sjekke hele planbestemmelsen opp mot lovverket.

### Konsept
Konseptet går ut på å utforske hvordan KI kan sjekke en planbestemmelse opp mot lovverket, henvise til relevante lover og avgjøre om bestemmelsen har hjemmel i forhold til lovverket.

### Problemstilling 
_Hvordan kan KI brukes til å vurdere om en planbestemmelse er i tråd med lovverket og identifisere eventuelle avvik på en presis og forståelig måte?_

## Proof of Concept 5 - Versjonsoversikt
### Bakgrunn
Det kommer nye dokumenter og versjoner gjennom hele prosessen, og det er vanskelig å holde styr på endringer som blir gjort underveis i planprosessen.

### Konsept
Konseptet går ut på å utforske hvordan KI kan brukes til å lage en versjonsoversikt for endringene som skjer i plandokumenter fortløpende underveis i planprosessen.

### Problemstilling
_Hvordan kan KI brukes til å identifisere og oppsummere endringer mellom ulike versjoner av plandokumenter på en måte som gir saksbehandlere en rask og informativ oversikt?_

## Proof of Concept 6 - Forenkling
### Bakgrunn
Planmateriale er omfattende og er preget av tungt og faglig språk som kan være vanskelig for innbyggere å tolke.

### Konsept
Konseptet går ut på å utforske hvordan KI kan brukes til å oppsummere virkningene av et planforslag for innbyggere uten planfaglig kompetanse.

### Problemstilling
_Hvordan kan KI brukes til å oppsummere et planforslag på en måte som gjør det enklere for innbyggere å forstå hvordan forslaget påvirker deres eiendom, nærmiljø og dagligliv?_ 

## Setup and run (Windows, PowerShell)

1. Create a virtual environment (recommended):

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

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the backend (from the `backend` folder):

PoC 1

```powershell
python file.py
```

PoC 2, 3, 4, 5 og 6

```powershell
python app.py
```

VS Code / Pylance notes

- Make sure VS Code is using the same Python interpreter where you installed the packages (`.venv` interpreter).
- Open the Command Palette (Ctrl+Shift+P) → `Python: Select Interpreter` → choose the `.venv` interpreter.
- After selecting the interpreter, Pylance should refresh and resolve `flask` imports.

If you want me to, I can create the venv and install packages now (I will run the commands in the terminal).
