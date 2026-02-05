from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")
    if not files:
        return jsonify({'error': 'Ingen filer mottatt'}), 400

    saved = []
    try:
        for f in files:
            if f and f.filename:
                filename = secure_filename(f.filename)
                path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                f.save(path)
                saved.append(filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'uploaded': saved}), 200

if __name__ == "__main__":
    app.run(debug=True)