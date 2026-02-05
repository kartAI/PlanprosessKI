from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

documents = []  # lagres i minne

@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")
    
    for file in files:
        path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)