
/**
 * Loads an HTML file and inserts it into the target element.
 * @param {string} elementId - The ID of the target element.
 * @param {string} filePath - Path to the HTML file to include.
 */
    function includeHTML(elementId, filePath) {
    fetch(filePath)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to load ${filePath}: ${response.status}`);
            }
            return response.text();
        })
        .then(data => {
            document.getElementById(elementId).innerHTML = data;
        })
        .catch(error => {
            console.error(error);
            document.getElementById(elementId).innerHTML = "<p style='color:red;'>Error loading content.</p>";
        });
    }

// Include header and footer
includeHTML("header", "header.html");

// Velger riktig backend-base URL for alle maskiner
const API_BASE =
window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:5000"
    : "http://localhost:5000";


const fileInputs = document.querySelectorAll('input[type="file"]');
fileInputs.forEach(input => {
    input.addEventListener('change', function(e) {
        const files = e.target.files;
        const nameElement = document.getElementById(e.target.id + '-name');
        if (!files || files.length === 0) {
            nameElement.textContent = 'Ingen fil valgt';
            nameElement.style.color = '#999';
        } else if (files.length === 1) {
            nameElement.textContent = files[0].name;
            nameElement.style.color = '#667eea';
        } else {
            nameElement.textContent = files.length + ' filer valgt';
            nameElement.style.color = '#667eea';
        }
    });
});

// Håndter skjema-innsending
const uploadForm = document.getElementById('uploadForm');
if (uploadForm) {
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        const files = document.getElementById('versjonsoversikt-fil').files;

        if (!files || files.length === 0) {
            // Ikke-blokkerende tilbakemelding
            showBanner('Vennligst velg minst én fil', 'error');
            return;
        }

        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }

        try {
            const response = await fetch(`${API_BASE}/upload`, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                // Ikke-blokkerende melding; redirect umiddelbart
                showBanner('Opplasting fullført — sender til alle endringer...', 'success');
                window.location.href = 'endring.html?t=' + Date.now();
            } else {
                const error = await response.text();
                showBanner('Feil ved opplasting: ' + error, 'error');
                console.error('Upload error:', error);
            }
        } catch (error) {
            showBanner('Kunne ikke koble til serveren. Er Flask-serveren kjørende?', 'error');
            console.error('Error:', error);
        }
    });
}

// Hent dokumenter fra backend - kun på endring.html
async function loadDocuments() {
    try {
        // Bruk no-store + cache busting for å unngå gammel liste
        const response = await fetch(`${API_BASE}/documents?t=${Date.now()}`, {
            method: 'GET',
            cache: 'no-store'
        });
        const documents = await response.json();
        
        const documentsList = document.getElementById('file-list');
        if (documentsList) {
            documentsList.innerHTML = documents.map(doc => 
                `<a href="${API_BASE}/upload/${doc}" target="_blank" class="file-list">${doc}</a>`
            ).join('<br>');
        }
    } catch (error) {
        console.error('Feil ved henting av dokumenter:', error);
    }
}

// Hent input og tekstfelt
const fileInput = document.getElementById("versjonsoversikt-fil");
const fileNameDisplay = document.getElementById("versjonsoversikt-navn");

// Oppdater tekst når bruker velger fil
fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
        const names = Array.from(fileInput.files).map(f => f.name).join(', ');
        fileNameDisplay.textContent = names;
    } else {
        fileNameDisplay.textContent = "Ingen fil valgt";
    }
});

// Enkel ikke-blokkerende bannermelding
function showBanner(message, type = 'info') {
    const existing = document.getElementById('upload-banner');
    if (existing) existing.remove();

    const banner = document.createElement('div');
    banner.id = 'upload-banner';
    banner.className = 'upload-banner upload-banner--' + (type || 'info');
    banner.textContent = message;

    document.body.appendChild(banner);
    setTimeout(() => {
        // fade out then remove for a smooth UX
        banner.style.opacity = '0';
        banner.style.transform = 'translateX(-50%) translateY(-6px)';
        setTimeout(() => banner.remove(), 250);
    }, 3000);
}

//Funksjon som laster inn opplastede filer
function loadUploadedFiles() {
    fetch("http://127.0.0.1:5000/list-uploads")
        .then(res => res.json())
        .then(files => {
            const container = document.getElementById("file-list");
            container.innerHTML = "";

            if (files.length === 0) {
                container.innerHTML = "<p>Ingen filer er lastet opp enda</p>";
                return;
            }

            files.forEach(file => {
                const div = document.createElement("div");
                div.textContent = file;
                container.appendChild(div);
            });
        })
        .catch(err => console.error("Feil ved henting av filer:", err));
}

loadUploadedFiles();



