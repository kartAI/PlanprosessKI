from flask import Flask, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file1' not in request.files or 'file2' not in request.files or 'file3' not in request.files:
        return 'No file part', 400
    files = [request.files['file1'], request.files['file2'], request.files['file3']]
    for file in files:
        if file.filename == '':
            return 'No selected file', 400
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return 'Files uploaded successfully', 200

if __name__ == '__main__':
    app.run(debug=True)