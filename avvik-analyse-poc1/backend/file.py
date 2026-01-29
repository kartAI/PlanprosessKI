from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import json
import os

from extract_info import read_pdf
from services.analysis_service import extract_info_from_text
from services.comparison_service import compare_documents

app = Flask(__name__)
CORS(app)  # Tillater forespørsler fra frontend

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

def _json_dump(value) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)

@app.route('/upload', methods=['POST'])
def upload_file():
    #sjekker at alle tre filene er inkludert
    if 'file1' not in request.files or 'file2' not in request.files or 'file3' not in request.files:
        return 'No file part', 400
    files = [request.files['file1'], request.files['file2'], request.files['file3']]
    
    for file in files:
        #sjekker at filen har et navn
        if file.filename == '':
            return 'No selected file', 400
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        
        #sjekker om filen allerede eksisterer
        if not os.path.exists(file_path):
            #lagrer filen i upload
            file.save(file_path)
    
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
    pdf_path_1 = UPLOAD_FOLDER / "Planbeskrivelse3-Flere-avvik-med-bestemmelse.pdf"
    pdf_path_2 = UPLOAD_FOLDER / "Reguleringsbestemmelser.pdf"
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

    result_1 = extract_info_from_text(plan_text_1)
    result_2 = extract_info_from_text(plan_text_2)
    result_3 = extract_info_from_text(plan_text_3)

    comparison = compare_documents(
        plan_text_2,
        plan_text_1,
        plan_text_3,
        doc1_name="Planbestemmelse",
        doc2_name="Planbeskrivelse",
        doc3_name="Plankart"
    )

    terminal_output = "\n".join([
        str(comparison)
    ])

    return jsonify({
        "doc_names": {
            "doc1": "Planbeskrivelse3-Flere-avvik-med-bestemmelse",
            "doc2": "Reguleringsbestemmelser",
            "doc3": "Plankart (JSON)"
        },
        "extractions": {
            "planbeskrivelse": result_1,
            "reguleringsbestemmelser": result_2,
            "plankart": result_3
        },
        "comparison": comparison,
        "terminal_output": terminal_output
    }), 200

# Kjør appen
if __name__ == '__main__':
    app.run(debug=True)