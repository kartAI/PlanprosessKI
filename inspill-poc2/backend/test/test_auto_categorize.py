import sys
import os

# Legger til parent-mappen (backend/) i søkestien
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.analysis_services import generate_categories
# ...resten av koden...

def test_generate_categories():
    texts = [
        "Filnavn: privatperson. Det blir mye støy økt trafikk fra byggeplassen.",
        "Filnavn: kommune. Vi er bekymret for økt trafikk og dårligere luftkvalitet.",
        "Filnavn: NVE. Solforholdene blir dårligere på grunn av byggehøyden."
    ]

    result = generate_categories(texts)

    print("\n=== KATEGORIER FRA KI ===")
    print(result)

    assert "kategorier" in result
    assert isinstance(result["kategorier"], list)
    assert len(result["kategorier"]) >= 1

    first = result["kategorier"][0]
    assert "kategori" in first
    assert "beskrivelse" in first