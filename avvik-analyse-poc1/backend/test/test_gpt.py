import sys
from pathlib import Path

# Legg til backend-mappen på sys.path
backend_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(backend_dir))

from services.analysis_service import extract_info_from_text
from extract_info import read_pdf

pdf_path = backend_dir / "uploads" / "Planbeskrivelse3-Flere-avvik-med-bestemmelse.pdf"
plan_text = read_pdf(str(pdf_path))

result = extract_info_from_text(plan_text)
print(result)