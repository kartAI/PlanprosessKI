#laster inn og importer biblioteker
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from services.diff_analyse import analyse_all_diff


app = Flask(__name__)
CORS(app)

if __name__ == "__main__":
    app.run(debug=True)

