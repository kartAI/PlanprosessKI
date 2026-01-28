from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Tillater forespørsler fra frontend

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_file():
    #sjekker at alle tre filene er inkludert
    if 'file1' not in request.files or 'file2' not in request.files or 'file3' not in request.files:
        return 'No file part', 400
    files = [request.files['file1'], request.files['file2'], request.files['file3']]
    
    for file in files:
        #sjekker at filen har et navn
        if file.filename == '':
            return 'No selected file', 400
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        
        #sjekker om filen allerede eksisterer
        if not os.path.exists(file_path):
            #lagrer filen i upload
            file.save(file_path)
    
    return 'Files uploaded successfully', 200

@app.route('/files', methods=['GET'])
def get_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify(files)

@app.route('/file-content', methods=['GET'])
def get_file_content():
    files_list = os.listdir(app.config['UPLOAD_FOLDER'])
    file_contents = {}
    
    for filename in files_list:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_contents[filename] = f.read()
        except:
            file_contents[filename] = f'[Kunne ikke lese fil: {filename}]'
    
    return jsonify(file_contents)

# Kjør appen
if __name__ == '__main__':
    app.run(debug=True)