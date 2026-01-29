# PlanprosessKI
Repo for Grupp 7 - 2026


Setup and run (Windows, PowerShell)

1) Create a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies:

```powershell
pip install -r requirements.txt
```

3) Run the backend (from the `backend` folder):

```powershell
python file.py
```

VS Code / Pylance notes

- Make sure VS Code is using the same Python interpreter where you installed the packages (`.venv` interpreter).
- Open the Command Palette (Ctrl+Shift+P) → `Python: Select Interpreter` → choose the `.venv` interpreter.
- After selecting the interpreter, Pylance should refresh and resolve `flask` imports.

If you want me to, I can create the venv and install packages now (I will run the commands in the terminal).
