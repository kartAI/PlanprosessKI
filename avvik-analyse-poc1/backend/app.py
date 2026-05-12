from ast import compare

from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import json
import os

from read_pdf import read_pdf
from services.comparison_service import compare_documents

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / 'uploads'
JSON_FOLDER = BASE_DIR / 'json'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)

def _read_text_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        text = read_pdf(str(path))
    else:
        text = path.read_text(encoding="utf-8", errors="ignore")
    return text[:5000]

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file1' not in request.files or 'file2' not in request.files:
        return 'Missing files', 400

    planbestemmelse = request.files['file1']
    planbeskrivelse = request.files['file2']

    if planbestemmelse.filename == '' or planbeskrivelse.filename == '':
        return 'No selected file', 400

    # Slett tidligere opplastede pdf-filer
    for path in UPLOAD_FOLDER.glob('*.pdf'):
        path.unlink()

    planbestemmelse.save(UPLOAD_FOLDER / "Planbestemmelse.pdf")
    planbeskrivelse.save(UPLOAD_FOLDER / "Planbeskrivelse.pdf")

    return 'Files uploaded successfully', 200

@app.route('/file-content', methods=['GET'])
def get_file_content():
    contents = {}

    if UPLOAD_FOLDER.exists():
        for path in sorted(UPLOAD_FOLDER.iterdir()):
            if path.is_file():
                contents[path.name] = _read_text_file(path)

    json_path = JSON_FOLDER / "plankart.json"
    if json_path.exists() and json_path.name not in contents:
        contents[json_path.name] = _read_text_file(json_path)

    return jsonify(contents), 200

@app.route('/analysis-results', methods=['GET'])
def analysis_results():
    pdf_path_1 = UPLOAD_FOLDER / "Planbestemmelse.pdf"
    pdf_path_2 = UPLOAD_FOLDER / "Planbeskrivelse.pdf"
    json_path = JSON_FOLDER / "plankart.json"

    missing = []
    if not pdf_path_1.exists():
        missing.append(str(pdf_path_1))
    if not pdf_path_2.exists():
        missing.append(str(pdf_path_2))
    if not json_path.exists():
        missing.append(str(json_path))

    if missing:
        return jsonify({
            "error": "Mangler nødvendige filer for analyse.",
            "missing": missing
        }), 404

    plan_text_1 = read_pdf(str(pdf_path_1))
    plan_text_2 = read_pdf(str(pdf_path_2))

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
            plan_text_3 = json.dumps(json_data, indent=2, ensure_ascii=False)
    except json.JSONDecodeError as e:
        return jsonify({
            "error": "JSON-filen er korrupt.",
            "details": str(e)
        }), 400

    # Bruk simple_compare eller compare_documents
    comparison = compare_documents(
        plan_text_1,
        plan_text_2,
        plan_text_3
    )

    return jsonify({
        "comparison": comparison,
        "terminal_output": comparison
    }), 200

# Kjører appen
if __name__ == '__main__':
    app.run(debug=True)