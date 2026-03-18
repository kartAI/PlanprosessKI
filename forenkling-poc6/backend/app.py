# Importerer nødvendige biblioteker og moduler
from flask import Flask, request, jsonify, send_from_directory
from services.for_me_analyse import for_me_analyse
from services.read_pdf import read_pdf
from services.tools import get_address_data, clear_uploads
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import json

# Oppretter Flask-app og aktiverer CORS for å tillate forespørsler fra Frontend
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Setter opp opplastingsmappe
UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

# Global liste for å holde styr på siste opplastede filer i runtime
LAST_UPLOADS = []

# Endepunkt for filopplasting (kun én fil tillatt)
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")

    if not file or not file.filename:
        return jsonify({'error': 'Ingen fil mottatt'}), 400

    saved = []

    try:
        clear_uploads(UPLOAD_FOLDER)
        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)
        saved.append(filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    global LAST_UPLOADS
    LAST_UPLOADS = saved[:]

    return jsonify({'uploaded': saved}), 200

# for henting av adresser fra en lokal JSON-fil
@app.route("/properties", methods=["GET"])
def hent_adresser():
    with open("properties.json", encoding="utf-8") as f:
        return jsonify(json.load(f))


"""
@app.route("/for-me-analysis", methods=["GET"])
def for_me_analysis():
    uplodes_dir = Path(app.config["UPLOAD_FOLDER"])
    document = read_pdf(str(path))
    address = 

    resultat = for_me_analyse(address,document)
"""
    
if __name__ == "__main__":
    app.run(debug=True)

#For å skrive det ut i terminalen, ps, flytt app.run under.
"""
    result = for_me_analyse()
    print(result)
"""

