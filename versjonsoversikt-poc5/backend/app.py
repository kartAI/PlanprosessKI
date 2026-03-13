# Laster inn og importer biblioteker
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from services.diff_analyse import analyse_all_diff, compare_versions
from werkzeug.utils import secure_filename
from pathlib import Path
from services.pdf_reader import read_pdf

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

# Håndter opplastning av fil
@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")
    if not files:
        return jsonify({'error': 'Ingen filer mottatt'}), 400

    saved = []
    duplicates = []
    try:
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

    response = {'uploaded': saved}
    if duplicates:
        response['duplicates'] = duplicates
        
    return jsonify(response), 200

# Frontend kan hente en fil
@app.route('/uploads/<filename>', methods=['GET'])
def serve_file(filename):
    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    
# Leser filene i /uploads og gjør dem om til json
@app.route('/list-uploads', methods=['GET'])
def list_uploads():
    try:
        files = os.listdir(app.config["UPLOAD_FOLDER"])
        files = [f for f in files if not f.startswith('.')]  # fjern skjulte filer
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Slette en fil i uploads
@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if os.path.exists(path):
            os.remove(path)
            return jsonify({'message': 'File deleted'}), 200
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# Håndter analyse av alle PDF-filer i uploads        
@app.route('/all-changes-analysis', methods=['GET'])
def all_changes():
    pdfs = list(UPLOAD_FOLDER.glob("*.pdf"))
    if not pdfs:
        return jsonify({"error": "Ingen PDF funnet i uploads"}), 400

    documents = []
    for pdf in pdfs:
        text = read_pdf(str(pdf))
        documents.append({
            "filename": pdf.name,
            "text": text,
        })

    result = analyse_all_diff(documents)
    return jsonify(result), 200

# Håndterer sammenligning analysen av to spesifikke versjoner
@app.route('/compare-versions-analysis', methods=['POST'])
def compare_documents():
    if 'document1' not in request.files or 'document2' not in request.files:
        return jsonify({'error': 'Manglende filer'}), 400

    text1 = read_pdf(request.files['document1'].stream)
    text2 = read_pdf(request.files['document2'].stream)
    
    result = compare_versions(text1, text2)
    return jsonify(result), 200
    

if __name__ == "__main__":
    app.run(debug=True)
