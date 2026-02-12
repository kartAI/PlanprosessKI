from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import os
from services.analysis_service import extract_checklist_points, checklist_text, check_document_against_checklist
from read_pdf import read_pdf

app = Flask(__name__)
CORS(app)

# Mappe for opplastede filer
UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

# Keep track of the latest upload in this runtime.
LAST_UPLOADS = []

def _clear_uploads(folder: Path) -> None:
    for item in folder.iterdir():
        if item.is_file():
            item.unlink(missing_ok=True)

#tar imot én fil fra frontend, sjekker om den finnes fra før, og lagrer den hvis den er ny
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")

    if not file:
        return jsonify({'error': 'Ingen fil mottatt'}), 400

    if not file.filename:
        return jsonify({'error': 'Filen mangler filnavn'}), 400

    try:
        # Slett gamle filer først (samme som i første app.py)
        _clear_uploads(UPLOAD_FOLDER)

        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        file.save(path)

        # Oppdater siste opplastning
        global LAST_UPLOADS
        LAST_UPLOADS = [filename]

        return jsonify({'uploaded': [filename]}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#returnerer en liste over alle filer i uploads-mappen
@app.route("/documents", methods=["GET"])
def get_documents():
    docs = [f.name for f in UPLOAD_FOLDER.iterdir() if f.is_file()]
    return jsonify(docs), 200

#Server en spesifikk fil fra uploads-mappen.
@app.route("/uploads/<filename>", methods=["GET"])
def serve_file(filename):
    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    except Exception:
        return jsonify({"error": "Filen finnes ikke"}), 404

@app.route("/checklist", methods=["GET"])
def get_checklist():
    try:
        points = extract_checklist_points(checklist_text)
        return jsonify({"checklist": points}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#returner KI analyse
@app.route("/analysis", methods=["GET"])
def get_analysis():
    pdf_files = [f for f in UPLOAD_FOLDER.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]

    if not pdf_files:
        return jsonify({"error": "Ingen PDF funnet i uploads"}), 400

    path = pdf_files[0]
    
    try:
        # Les dokumentet
        document_text = read_pdf(str(path))
        
        # Hent sjekkliste
        checklist_points = extract_checklist_points(checklist_text)
    
        # Kjør analysen
        resultat = check_document_against_checklist(document_text, checklist_points)
        
        return jsonify(resultat), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)