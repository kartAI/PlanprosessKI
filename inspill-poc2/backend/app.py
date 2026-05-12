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
    summarize_category,
    classify_documents
)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

# Holder styr på sist opplastede dokumenter (kun filnavn)
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

# Liste over dokumenter
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

# FULL KI-ANALYSE AV ALLE PDF-ER
# ---------------------------------------------------------
@app.route("/analysis", methods=["GET"])
def analysis():
    if not LAST_UPLOADS:
        return jsonify({"error": "Ingen opplastede dokumenter"}), 400

    upload_dir = Path(app.config["UPLOAD_FOLDER"])
    pdf_files = [upload_dir / name for name in LAST_UPLOADS if name.lower().endswith(".pdf")]
    pdf_files = [p for p in pdf_files if p.exists()]

    if not pdf_files:
        return jsonify({"error": "Ingen PDF-filer funnet"}), 400

    documents = []

    # 1. Ekstraher tekst og oppsummer hvert dokument
    for pdf in pdf_files:
        try:
            text = read_pdf(str(pdf))
            summary = summarize_single_document(text)
            documents.append({
                "filename": pdf.name, 
                "summary": summary})
        except Exception as e:
            documents.append({"filename": pdf.name, "summary": f"[Feil: {e}]"})

    summaries = [d["summary"] for d in documents]

    # 2. Generer kategorier fra innholdet
    kategorier = generate_categories(summaries)

    # 3. Klassifiser inspill inn i kategoriene
    classification = classify_documents(documents, kategorier)
    
    # 4. Bygg kategoriliste
    category_documents = {k: [] for k in kategorier}
    category_summaries_input = {k: [] for k in kategorier}

    for doc in documents:
        assigned = classification.get(doc["filename"], [])
        for cat in assigned:
            if cat in category_documents:
                category_documents[cat].append(doc["filename"])
                category_summaries_input[cat].append(doc["summary"])

    # 5. Felles oppsummering
    combined_summary = summarize_all_documents(summaries)

    # 6. Oppsummering per kategori
    category_summaries = {
        name: summarize_category(name, sums)
        for name, sums in category_summaries_input.items()
    }

    # 7. Returner alt til frontend
    return jsonify({
        "documents": [{"filename": d["filename"]} for d in documents],
        "auto_categories": {"kategorier": [{"navn": k} for k in kategorier]},
        "category_documents": category_documents,
        "combined_summary": combined_summary,
        "category_summaries": category_summaries
    }), 200

if __name__ == "__main__":
    app.run(debug=True)

