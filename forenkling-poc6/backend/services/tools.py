import json
from pathlib import Path
from pypdf import PdfReader

# Sletter alle filer i uploads-mappen
def clear_uploads(folder: Path) -> None:
    for item in folder.iterdir():
        if item.is_file():
            item.unlink(missing_ok=True)

# Trekker ut koordinater til adressen fra properties.json
def get_address_data(address: str) -> dict:
    """Henter addressdata fra properties.json"""
    properties_path = Path(__file__).resolve().parent.parent / "properties.json"

    with open(properties_path, encoding="utf-8") as f:
        properties = json.load(f)

    address_data = next((p for p in properties if p["address"] == address), None)
    if not address_data:
        raise KeyError(f"Adresse '{address}' ikke funnet")

    return address_data


# Henter informasjon fra PDF og gjør det om til tekst
def read_pdf(path: str) -> str:
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

