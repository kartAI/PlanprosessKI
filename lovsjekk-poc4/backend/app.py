from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import os
from services.analysis_services import law_classification
from read_pdf import read_pdf

app = Flask(__name__)
CORS(app)

# Setter opp opplastingsmappe: lager "uploads" hvis den ikke finnes, og lagrer stien i app-konfigurasjonen.
UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

# Holder styr på siste opplastede filer i runtime
LAST_UPLOADS = []

# Hjelpefunksjon: sletter alle filer i upload-mappen
def _clear_uploads(folder: Path) -> None:
    for item in folder.iterdir():
        if item.is_file():
            item.unlink(missing_ok=True)

# Fjerner gamle filer, håndterer duplikater og lagrer nye
@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")
    if not files:
        return jsonify({'error': 'Ingen filer mottatt'}), 400

    saved = []
    duplicates = []
    try:
        # Slett gamle filer før opplasting
        _clear_uploads(UPLOAD_FOLDER)
        for f in files:
            if f and f.filename:
                filename = secure_filename(f.filename)
                path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                
                # Sjekk om filen allerede finnes
                if os.path.exists(path):
                    duplicates.append(filename)
                else:
                    f.save(path)
                    saved.append(filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    global LAST_UPLOADS
    LAST_UPLOADS = saved[:]

    response = {'uploaded': saved}
    if duplicates:
        response['duplicates'] = duplicates
    
    return jsonify(response), 200

# Endepunkt: hent liste over siste opplastede dokumenter
@app.route('/documents', methods=['GET'])
def get_documents():
    try:
        return jsonify(LAST_UPLOADS)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>', methods=['GET'])
def serve_file(filename):
    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    
@app.route('/analysis', methods=['GET'])
def get_bestemmelse(): #husk endre navn!

    #hvis ikke ligger fil i uploads
    if not LAST_UPLOADS:
        return jsonify({"error": "Ingen PDF funnet i uploads"}), 400

    #hent filen som ligger i uploads
    path = UPLOAD_FOLDER / LAST_UPLOADS[0]
    
    try:
        # Les dokumentet
        document_text = read_pdf(str(path))
    
        # Kjør analysen
        resultat = law_classification(document_text)
        
        #midlertidig printing av resultat fra law_classification()
        #return jsonify(resultat), 200
        
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start server i debug-modus
if __name__ == "__main__":
    app.run(debug=True)