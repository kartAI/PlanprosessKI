import os
from unittest import result
from flask import Flask, app, request, jsonify, send_from_directory
from flask_cors import CORS
from services.read_pdf import read_pdf
from services.for_me_analyse import for_me_analyse

app = Flask (__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

#her legges app routes

if __name__ == "__main__":
    app.run(debug = True)

"""
#For å skrive det ut i terminalen, ps, flytt app.run under.s
    result = for_me_analyse()
    print(result)
"""