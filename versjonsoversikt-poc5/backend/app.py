# Laster inn og importer biblioteker
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from services.diff_analyse import analyse_all_diff, compare_versions
from werkzeug.utils import secure_filename
from pathlib import Path
from services.pdf_reader import read_pdf
from services.curr_analyse import analyse_meetings

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

MEETINGS_FOLDER = Path(__file__).parent / "meetings"

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
    
# Håndter KI-analyse av møtereferater 
@app.route('/current_analysis', methods=['GET'])
def current_analyses():
    meetings_dir = MEETINGS_FOLDER
    try:
        # Les alle møtereferat-filer fra mappen
        files = [f for f in os.listdir(meetings_dir) if os.path.isfile(os.path.join(meetings_dir, f))]
        meeting_texts = []
        for filename in files:
            file_path = os.path.join(meetings_dir, filename)
            meeting_texts.append(read_pdf(file_path))  # les PDF til tekst

        all_meetings = "\n\n".join(meeting_texts)  # Samle all tekst til én streng

        # Kjør KI-analysen på samlet tekst
        resultat = analyse_meetings(all_meetings)
        
        return jsonify(resultat), 200       
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

# Test direkte i terminalen, husk å flytt "app.run(debug=True)" under. 
"""if __name__ == "__main__":
    # Test direkte i terminalen
    meetings_dir = MEETINGS_FOLDER
    files = [f for f in os.listdir(meetings_dir) if os.path.isfile(os.path.join(meetings_dir, f))]
    meeting_texts = []
    for filename in files:
        file_path = os.path.join(meetings_dir, filename)
        meeting_texts.append(read_pdf(file_path))
    all_meetings = "\n\n".join(meeting_texts)
    print(analyse_meetings(all_meetings))"""
    
    
    
