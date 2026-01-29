import sys
import json
from pathlib import Path

# Legg til backend-mappen på sys.path
backend_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(backend_dir))

from services.analysis_service import extract_info_from_text
from extract_info import read_pdf

uploads_dir = backend_dir / "uploads"
json_dir = backend_dir / "json"

# Les PDF-dokumenter
pdf_path_1 = uploads_dir / "Planbeskrivelse3-Flere-avvik-med-bestemmelse.pdf"
pdf_path_2 = uploads_dir / "Reguleringsbestemmelser.pdf"

plan_text_1 = read_pdf(str(pdf_path_1))
plan_text_2 = read_pdf(str(pdf_path_2))

print("PDF Dokument 1 hentet")
print("PDF Dokument 2 hentet")

# Les JSON-fil med feilhåndtering
json_path = json_dir / "plankart.json"
if not json_path.exists():
    print(f"FEIL: JSON-fil ikke funnet på {json_path}")
    sys.exit(1)

try:
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
        plan_text_3 = json.dumps(json_data, indent=2, ensure_ascii=False)
    print("JSON Dokument hentet")
except json.JSONDecodeError as e:
    print(f"FEIL: JSON-filen er korrupt: {e}")
    sys.exit(1)

# Ekstrahér info fra alle tre dokumenter
result_1 = extract_info_from_text(plan_text_1)
result_2 = extract_info_from_text(plan_text_2)
result_3 = extract_info_from_text(plan_text_3)

print("\n=== RESULTAT PLANBESKRIVELSE ===")
print(result_1)
print("\n=== RESULTAT REGULERINGSBESTEMMELSER ===")
print(result_2)
print("\n=== RESULTAT PLANKART (JSON) ===")
print(result_3)

from services.comparison_service import compare_documents

result = compare_documents(
    plan_text_1,
    plan_text_2,
    plan_text_3,
    doc1_name="Planbeskrivelse",
    doc2_name="Planbestemmelser",
    doc3_name="Plankart"
)

print("\n=== SAMMENLIGNINGSRESULTAT ===")
print(result)