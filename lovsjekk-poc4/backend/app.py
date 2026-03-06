#importerer nødvendige biblioteker og moduler
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import os
from read_pdf import read_pdf
from services.analysis_services import law_classification, get_filtered_law_data, analyse_law_conflict  

#oppretter Flask-app og aktiverer CORS for å tillate forespørsler fra frontend
app = Flask(__name__)
CORS(app)

# Setter opp opplastingsmappe: lager "uploads" hvis den ikke finnes, og lagrer stien i app-konfigurasjonen.
UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True) #oppretter om ikke allerede eksisterer
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

#Global liste for å holde styr på siste opplastede filer i runtime
LAST_UPLOADS = []

# Hjelpefunksjon: Sletter alle filer i uploads-mappen for å unngå opphopning av gamle filer
def _clear_uploads(folder: Path) -> None:
    for item in folder.iterdir():
        if item.is_file():
            item.unlink(missing_ok=True)  # Slett filen trygt


# Endepunkt for filopplasting (kun én fil tillatt)
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")  # Hent én enkelt fil (ikke liste)
    if not file or not file.filename:
        return jsonify({'error': 'Ingen fil mottatt'}), 400

    saved = []  # Liste over lagrede filer (vil inneholde kun én)

    try:
        # Slett gamle filer før opplasting
        _clear_uploads(UPLOAD_FOLDER)
        
        # Behandle den ene filen
        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)  # Lagre filen
        saved.append(filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    global LAST_UPLOADS
    LAST_UPLOADS = saved[:]  # Oppdater med den ene filen

    # Returner respons med den lagrede filen
    return jsonify({'uploaded': saved}), 200


# Endepunkt: hent liste over siste opplastede dokumenter
@app.route('/documents', methods=['GET'])
def get_documents():
    try:
        return jsonify(LAST_UPLOADS) #returnerer listen som JSON
    except Exception as e:
        return jsonify({'error': str(e)}), 500 #feil ved henting av dokumenter


#Endepunkt for å servere filer fra uploads-mappen
@app.route('/uploads/<filename>', methods=['GET'])
def serve_file(filename):
    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename) #send filen
    except Exception as e:
        return jsonify({'error': str(e)}), 404 #feil hvis fil ikke finnes


#Endepunkt for analyse: leser siste opplastede PDF, kjører KI-analyse og returnerer filtrert data
@app.route('/analysis', methods=['GET'])
def get_bestemmelse():  # Husk å endre navn!

    # sjekk om det finnes opplastede filer, hvis ikke returner feil
    if not LAST_UPLOADS:
        return jsonify({"error": "Ingen PDF funnet i uploads"}), 400

    # Hent sti til første opplastede fil
    path = UPLOAD_FOLDER / LAST_UPLOADS[0]
    
    try:
        # Les tekst fra PDF-filen
        document_text = read_pdf(str(path))
    
        #Steg 1: Kjør KI-basert klassifisering for å idtentifisere relevante lover
        resultat = law_classification(document_text)
        
        #Steg 2: Kjør filtrering mot XML for å trekke ut relevant lovtekst
        xml_path = "lovverk.xml"  #sti til XML-fil
        filtered = get_filtered_law_data(resultat, xml_path)

        #steg 3: sjekk for strid
        conflict_analyse = analyse_law_conflict(document_text, filtered)

        #Valgfritt: print resultater til terminal
        #print("resultat fra klassifisering:",resultat) 
        #print("resultat fra filtrering:", filtered)  

        #returnerer filtrert data som JSON-respons
        return jsonify(conflict_analyse), 200       
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Start server i debug-modus når filen kjøres direkte
if __name__ == "__main__":
    app.run(debug=True)