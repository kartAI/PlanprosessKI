# Importerer nødvendige biblioteker og moduler
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import os
from services.read_pdf import read_pdf
from services.summary_analyse import summary_analyse

# Oppretter Flask-app og aktiverer CORS for å tillate forespørsler fra Frontend
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Setter opp opplastingsmappe
UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

# Global liste for å holde styr på siste opplastede filer i runtime
LAST_UPLOADS = []

# Hjelpefunksjon: Sletter alle filer i uploads-mappen
def _clear_uploads(folder: Path) -> None:
    for item in folder.iterdir():
        if item.is_file():
            item.unlink(missing_ok=True)

# Endepunkt for filopplasting (kun én fil tillatt)
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")

    if not file or not file.filename:
        return jsonify({'error': 'Ingen fil mottatt'}), 400

    saved = []

    try:
        _clear_uploads(UPLOAD_FOLDER)
        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)
        saved.append(filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    global LAST_UPLOADS
    LAST_UPLOADS = saved[:]

    return jsonify({'uploaded': saved}), 200

# Endepunkt: hent liste over siste opplastede dokumenter
@app.route('/documents', methods=['GET'])
def get_documents():
    try:
        return jsonify(LAST_UPLOADS) # Returnerer listen som JSON
    except Exception as e:
        return jsonify({'error': str(e)}), 500 # Feil ved henting av dokumenter

#Endepunkt for å servere filer fra uploads-mappen
@app.route('/uploads/<filename>', methods=['GET'])
def serve_file(filename):
    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename) #send filen
    except Exception as e:
        return jsonify({'error': str(e)}), 404 #feil hvis fil ikke finnes


#endepunkt for summary_analyse
@app.route("/summary-analysis", methods=["GET"])
def summary():
    if not LAST_UPLOADS:
        return jsonify({'error': 'Ingen fil lastet opp'}), 400
    
    path = os.path.join(app.config["UPLOAD_FOLDER"], LAST_UPLOADS[0])
    
    document = read_pdf(path)

    result = summary_analyse(document)
    return jsonify(result), 200

#For å skrive det ut i terminalen, ps, flytt app.run under.
"""
    result = for_me_analyse()
    print(result)
"""

if __name__ == "__main__":
    app.run(debug=True)

