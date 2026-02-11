// Velger riktig backend-base URL for alle maskiner
const API_BASE =
window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:5000"
    : "http://localhost:5000";


const fileInputs = document.querySelectorAll('input[type="file"]');
fileInputs.forEach(input => {
    input.addEventListener('change', function(e) {
        const files = e.target.files;  // ← Endre fra .file til .files
        const nameElement = document.getElementById(e.target.id + '-name');
        if (!files || files.length === 0) {
            nameElement.textContent = 'Ingen fil valgt';
            nameElement.style.color = '#999';
        } else if (files.length === 1) {
            nameElement.textContent = files[0].name;
            nameElement.style.color = '#667eea';
        } else {
            // Avvis flere filer
            nameElement.textContent = 'Kun ett dokument er tillatt';
            nameElement.style.color = '#e74c3c';
            e.target.value = ''; // Tøm inputen
        }
    });
});

// Håndter skjema-innsending
const uploadForm = document.getElementById('uploadForm');
if (uploadForm) {
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        const files = document.getElementById('planbeskrivelse').files;  

        if (!files || files.length === 0) {
            showBanner('Vennligst velg én fil', 'error');
            return;
        }

        // Valider at kun ett dokument er valgt
        if (files.length > 1) {
            showBanner('Kun ett dokument er tillatt', 'error');
            return;
        }

        // Legg til den en fil
        formData.append('file', files[0]);  

        try {
            const response = await fetch(`${API_BASE}/upload`, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                showBanner('Opplasting fullført — sender til oppsummering...', 'success');
                window.location.href = 'sjekkliste.html?t=' + Date.now();
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

// Hent dokumenter fra backend - kun på oppsummering.html
async function loadDocuments() {
    try {
        // Bruk no-store + cache busting for å unnga gammel liste
        const response = await fetch(`${API_BASE}/documents?t=${Date.now()}`, {
            method: 'GET',
            cache: 'no-store'
        });
        const documents = await response.json();
        
        const documentsList = document.getElementById('documents-list');
        if (documentsList) {
            documentsList.innerHTML = documents.map(doc => 
                `<a href="${API_BASE}/uploads/${doc}" target="_blank" class="document-link">${doc}</a>`
            ).join('<br>');
        }
    } catch (error) {
        console.error('Feil ved henting av dokumenter:', error);
    }

}

// Hent og vis sjekklisten
async function loadChecklist() {
    try {
        const response = await fetch(`${API_BASE}/checklist`);
        const data = await response.json();
        
        const checklistElement = document.getElementById('checklist-list');
        if (checklistElement && data.checklist) {
            checklistElement.innerHTML = data.checklist.map(point => 
                `<li>${point}</li>`
            ).join('');
        }
    } catch (error) {
        console.error('Feil ved henting av sjekkliste:', error);
    }
}

const filnavn = "planbeskrivelse_m.pdf";
fetch(`${API_BASE}/uploads/${filnavn}`)
    .then(response => {
        if (!response.ok) throw new Error("Filen finnes ikke");
        return response.blob();
    })
    .then(blob => {
        // Vis filen, f.eks. som PDF i <iframe> eller last ned
        const url = URL.createObjectURL(blob);
        document.getElementById("pdfViewer").src = url;
    })
    .catch(error => {
        // Håndter feil
    alert(error.message);
    });

// Kall funksjonen når siden lastes
document.addEventListener('DOMContentLoaded', loadChecklist);

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
        banner.style.opacity = '0';
        banner.style.transform = 'translateX(-50%) translateY(-6px)';
        setTimeout(() => banner.remove(), 250);
    }, 3000);
}

