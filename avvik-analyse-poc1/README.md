# Bachelorprosjket - PlanprosessKI

Repo for Grupp 7 - 2026

## Hovedproblemstilling

Utforske hvordan KI kan brukes i en planprosess, med fokus på formidling, forståelse og kontroll av prosessen. Prosjektet skal utvikle proof-of-concepts som forenkler planprosessen for ulike aktører, inkludert innbyggere, høringsinstanser og fagfolk. Målet er å identifisere tekniske muligheter som gir konkret sluttbrukerverdi, og spisse løsningen mot spesifikke deler av planprosessen, for eksempel konsekvensutredning osv.

### Prosjektstruktur

KOMMER

## Proof of Concept 1 - Sjekk avvik mellom dokumenter i et planforslag

Planforslag består av plankart, planbestemmelser og planbeskrivelser, og det kan være vanskelig å sjekke om disse stemmer overens. Kan KI brukes til å identifisere avvik eller flagge potensielle konflikter mellom dokumentene i et planforslag?

## Proof of Concept 2 - Oppsummering av høringsinnspill

Det kan komme mange innspill og høringer knyttet til hver planendring som kan være tidkrevende og uoversiktlig å lese gjennom. Kan KI brukes til å gi en objektiv oppsummering av høringer og innspill, for å kategorisere og/eller trekke ut hva som er de viktigste punktene som går igjen?

## Proof of Concept 3 - Sjekkliste for planbeskrivelse

Det kan være utfordrende å sørge for at alle punktene i sjekklisten/malen (sjekkliste fra regjeringen, mal Kristiansand Kommune) er oppfylt i planbeskrivelsen. Kan KI brukes til å automatisk sjekke at kravene i sjekklisten er inkludert, eventuelt også oppfylt, i planbeskrivelsen?

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

PoC 2 og 3

```powershell
python app.py
```

VS Code / Pylance notes

- Make sure VS Code is using the same Python interpreter where you installed the packages (`.venv` interpreter).
- Open the Command Palette (Ctrl+Shift+P) → `Python: Select Interpreter` → choose the `.venv` interpreter.
- After selecting the interpreter, Pylance should refresh and resolve `flask` imports.

If you want me to, I can create the venv and install packages now (I will run the commands in the terminal).
