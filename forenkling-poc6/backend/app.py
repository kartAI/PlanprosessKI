from flask import Flask, request, jsonify, send_from_directory
from services.for_me_analyse import for_me_analyse
from services.read_pdf import read_pdf
from services.tools import get_address_data, clear_uploads
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

LAST_UPLOADS = []


@app.before_request
def log_request():
    print(f"\n[BEFORE_REQUEST] {request.method} {request.path}")
    print(f"  Content-Type: {request.content_type}")
    print(f"  Data size: {len(request.data)} bytes")
    if request.data:
        print(f"  Data: {request.data[:200]}")


@app.errorhandler(400)
def handle_400(e):
    print(f"[ERROR 400] {str(e)}")
    return jsonify({"error": f"Bad Request: {str(e)}"}), 400


@app.errorhandler(404)
def handle_404(e):
    print(f"[ERROR 404] {str(e)}")
    return jsonify({"error": "Endpoint not found"}), 404


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")

    if not file or not file.filename:
        return jsonify({"error": "Ingen fil mottatt"}), 400

    saved = []

    try:
        clear_uploads(UPLOAD_FOLDER)
        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)
        saved.append(filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    global LAST_UPLOADS
    LAST_UPLOADS = saved[:]

    return jsonify({"uploaded": saved}), 200


@app.route("/properties", methods=["GET"])
def hent_adresser():
    properties_path = Path(__file__).parent / "properties.json"
    with open(properties_path, encoding="utf-8") as f:
        return jsonify(json.load(f))


def _find_pdf_for_analysis() -> Path | None:
    if LAST_UPLOADS:
        candidate = UPLOAD_FOLDER / LAST_UPLOADS[0]
        if candidate.exists() and candidate.is_file():
            return candidate

    pdf_files = [p for p in UPLOAD_FOLDER.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"]
    if not pdf_files:
        return None

    return max(pdf_files, key=lambda p: p.stat().st_mtime)


@app.route("/uploads/<path:filename>", methods=["GET"])
def get_uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/latest-upload", methods=["GET"])
def latest_upload():
    pdf_file = _find_pdf_for_analysis()
    if not pdf_file:
        return jsonify({"filename": None}), 200
    return jsonify({"filename": pdf_file.name}), 200


@app.route("/for-meg", methods=["POST"])
def for_meg_analysis():
    try:
        data = request.get_json(silent=True) or {}
        print(f"[DEBUG] JSON data: {data}")

        address = (data.get("address") or data.get("adresse") or "").strip()
        print(f"[DEBUG] Address: {address}")

        if not address:
            return jsonify({"error": "Adresse er påkrevd"}), 400

        pdf_file = _find_pdf_for_analysis()
        print(f"[DEBUG] PDF valgt: {pdf_file}")

        if not pdf_file:
            return jsonify({"error": "Ingen planbestemmelse lastet opp - last opp PDF først"}), 400

        address_data = get_address_data(address)
        document = read_pdf(str(pdf_file))

        result = for_me_analyse(address_data, document)

        if isinstance(result, dict):
            return jsonify(result), 500

        parsed = json.loads(result)
        return jsonify(parsed), 200

    except KeyError as e:
        return jsonify({"error": f"Adresse ikke funnet: {str(e)}"}), 404
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Ugyldig JSON fra KI-respons: {str(e)}"}), 500
    except FileNotFoundError as e:
        return jsonify({"error": f"Fil ikke funnet: {str(e)}"}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Feil: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)