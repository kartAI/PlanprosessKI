from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from pathlib import Path


from read_pdf import read_pdf
from services.analysis_services import (
    summarize_single_document,
    generate_categories,
    summarize_all_documents,
    summarize_category
)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

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

#liste over dokumenter
@app.route('/documents', methods=['GET'])
def get_documents():
    try:
        files = os.listdir(app.config["UPLOAD_FOLDER"])
        # Filtrer bort mapper, bare ta filer
        files = [f for f in files if os.path.isfile(os.path.join(app.config["UPLOAD_FOLDER"], f))]
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>', methods=['GET'])
def serve_file(filename):
    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# FULL KI-ANALYSE AV ALLE PDF-ER
# ---------------------------------------------------------
@app.route("/analysis", methods=["GET"])
def analysis():
    upload_dir = Path(app.config["UPLOAD_FOLDER"])
    pdf_files = [p for p in upload_dir.iterdir() if p.suffix.lower() == ".pdf"]

    if not pdf_files:
        return jsonify({"error": "Ingen PDF-filer funnet"}), 400

    documents = []
    all_texts = []

    # 1. Ekstraher tekst + oppsummer hvert dokument
    for pdf in pdf_files:
        text = read_pdf(str(pdf))
        summary = summarize_single_document(text)

        documents.append({
            "filename": pdf.name,
            "text": text,
            "summary": summary
        })

        all_texts.append(text)


     # 2. Automatisk kategorisering
    auto = generate_categories(all_texts)

    # 3. Lag kategori → dokumentliste
    category_map = {cat["navn"]: [] for cat in auto["kategorier"]}

    for doc in documents:
        for cat in auto["kategorier"]:
            if any(word.lower() in doc["text"].lower() for word in cat["navn"].split()):
                category_map[cat["navn"]].append(doc["text"])

    # 4. Felles oppsummering
    combined_summary = summarize_all_documents([d["summary"] for d in documents])

    # 5. Oppsummering per kategori
    category_summaries = {
        name: summarize_category(name, texts)
        for name, texts in category_map.items()
    }
    # 6. Returner alt til frontend
    return jsonify({
        "documents": documents,
        "auto_categories": auto,
        "category_distribution": category_map,
        "combined_summary": combined_summary,
        "category_summaries": category_summaries
    }), 200

if __name__ == "__main__":
    app.run(debug=True)

