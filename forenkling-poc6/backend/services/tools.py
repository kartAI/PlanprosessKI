import json
# Sletter alle filer i uploads-mappen
def clear_uploads(folder: Path) -> None:
    for item in folder.iterdir():
        if item.is_file():
            item.unlink(missing_ok=True)

# Trekker ut kordinater til addressen fra properties.json
def get_address_data(address: str, properties_file: str = "../properties.json") -> dict:
    """Henter addressdata fra properties.json"""
    with open(properties_file, encoding="utf-8") as f:
        properties = json.load(f)

    address_data = next((p for p in properties if p["address"] == address), None)
    if not address_data:
        raise KeyError(f"Adresse '{address}' ikke funnet")

    return address_data
