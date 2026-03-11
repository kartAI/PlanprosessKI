
/**
 * Laster inn en HTML‑fil og setter den inn i mål‑elementet.
 * @param {string} elementId - ID‑en til mål‑elementet.
 * @param {string} filePath - Stien til HTML‑filen som skal inkluderes.
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

// Inkluderer header elementet HTML
includeHTML("header", "header.html");

// Velger riktig backend-base URL for alle maskiner
const API_BASE =
window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:5000"
    : "http://localhost:5000";

// Håndter skjema-innsending
const uploadForm = document.getElementById('uploadForm');
if (uploadForm) {
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        const files = document.getElementById('versjonsoversikt-fil').files;

        if (!files || files.length === 0) {
            // Ikke-blokkerende tilbakemelding hvis ingen fil er valgt
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
        // fade out på bannermelding for brukervennlig UX
        banner.style.opacity = '0';
        banner.style.transform = 'translateX(-50%) translateY(-6px)';
        setTimeout(() => banner.remove(), 250);
    }, 3000);
}

//Funksjon som laster inn opplastede filer
function loadUploadedFiles() {
    fetch(`${API_BASE}/list-uploads`)
        .then(res => res.json())
        .then(files => {
            const container = document.getElementById("file-list");
            container.innerHTML = "";

            if (files.length === 0) {
                container.innerHTML = "<p>Ingen filer er lastet opp enda</p>";
                return;
            }

            // For hver fil i uploads lager et HTML element med link og sletteknapp(div)
            files.forEach(file => {
                const div = document.createElement("div");
                div.className = "file-item";

                // Gjøre filer klikkbare
                const link = document.createElement("a");
                link.href = `${API_BASE}/uploads/${file}`;
                link.target = "_blank";
                link.textContent = file;
                link.className = "file-link";

                // Lage en sletteknapp for filer
                const deleteBtn = document.createElement("button");
                deleteBtn.textContent = "Slett";
                deleteBtn.className = "delete-btn";
                deleteBtn.onclick = () => deleteFile(file);

                // Legger filer til i DOM
                div.appendChild(link);
                div.appendChild(deleteBtn);
                container.appendChild(div);
            });
        })
        .catch(err => console.error("Feil ved henting av filer:", err));
}

//funksjon for å slette filer fra uploads
function deleteFile(filename) {
    if (confirm(`Er du sikker på at du vil slette ${filename}?`)) {
        fetch(`${API_BASE}/delete/${filename}`, {
            method: 'DELETE'
        })
        .then(res => res.json())
        .then(data => {
            if (data.message) {
                showBanner('Fil slettet', 'success');
                loadUploadedFiles(); // Oppdaterer uploads
            } else {
                showBanner('Feil ved sletting: ' + data.error, 'error');
            }
        })
        .catch(err => {
            showBanner('Feil ved sletting', 'error');
            console.error('Delete error:', err);
        });
    }
}

loadUploadedFiles();



