from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import json
import os

app = Flask(__name__)
CORS(app)

# Setter opp opplastingsmappe: lager "uploads" hvis den ikke finnes, og lagrer stien i app-konfigurasjonen.
UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

# Keep track of the latest upload in this runtime.
LAST_UPLOADS = []

def _clear_uploads(folder: Path) -> None:
    for item in folder.iterdir():
        if item.is_file():
            item.unlink(missing_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")
    if not files:
        return jsonify({'error': 'Ingen filer mottatt'}), 400

    saved = []
    duplicates = []
    try:
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

#liste over dokumenter
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

if __name__ == "__main__":
    app.run(debug=True)