from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
from services.analysis_service import extract_checklist_points, checklist_text

app = Flask(__name__)
CORS(app)

# Mappe for opplastede filer
UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)


#tar imot én fil fra frontend, sjekker om den finnes fra før, og lagrer den hvis den er ny
@app.route("/upload", methods=["POST"])
def upload():

    # Hent én fil
    f = request.files.get("file")
    if not f or not f.filename:
        return jsonify({"error": "Ingen fil mottatt"}), 400

    filename = secure_filename(f.filename)
    path = UPLOAD_FOLDER / filename

    # Sjekk om filen allerede finnes
    if path.exists():
        return jsonify({
            "uploaded": [],
            "duplicates": [filename]
        }), 200

    # Lagre ny fil
    f.save(path)

    return jsonify({
        "uploaded": [filename],
        "duplicates": []
    }), 200

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

# Returner sjekklisten
@app.route("/checklist", methods=["GET"])
def get_checklist():
    points = extract_checklist_points(checklist_text)  
    return jsonify({"checklist": points}), 200

if __name__ == "__main__":
    app.run(debug=True)