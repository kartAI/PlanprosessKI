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
        const files = document.getElementById('innspill').files;

        if (!files || files.length === 0) {
            // Ikke-blokkerende tilbakemelding
            showBanner('Vennligst velg minst én fil', 'error');
            return;
        }

        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }

        try {
            const response = await fetch('http://localhost:5000/upload', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                // Ikke-blokkerende melding; redirect umiddelbart
                showBanner('Opplasting fullført — sender til oppsummering...', 'success');
                window.location.href = 'oppsummering.html?t=' + Date.now();
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
        // Bruk no-store for å sikre at vi ikke får cached resultat
        const response = await fetch('http://localhost:5000/documents?t=' + Date.now(), {
            method: 'GET',
            cache: 'no-store'
        });
        const documents = await response.json();
        
        const documentsList = document.getElementById('documents-list');
        if (documentsList) {
            documentsList.innerHTML = documents.map(doc => 
                `<a href="http://localhost:5000/uploads/${doc}" target="_blank" class="document-link">${doc}</a>`
            ).join('<br>');
        }
    } catch (error) {
        console.error('Feil ved henting av dokumenter:', error);
    }
}

// Kall funksjonen når siden lastes
document.addEventListener('DOMContentLoaded', loadDocuments);

// Enkel ikke-blokkerende bannermelding
function showBanner(message, type = 'info') {
    const existing = document.getElementById('upload-banner');
    if (existing) existing.remove();

    const banner = document.createElement('div');
    banner.id = 'upload-banner';
    banner.textContent = message;
    banner.style.position = 'fixed';
    banner.style.top = '20px';
    banner.style.left = '50%';
    banner.style.transform = 'translateX(-50%)';
    banner.style.padding = '10px 18px';
    banner.style.borderRadius = '6px';
    banner.style.zIndex = 10000;
    banner.style.color = '#fff';
    banner.style.fontWeight = '600';
    banner.style.boxShadow = '0 4px 12px rgba(0,0,0,0.12)';
    banner.style.opacity = '0.95';

    if (type === 'error') banner.style.background = '#d32f2f';
    else if (type === 'success') banner.style.background = '#034E31';
    else banner.style.background = '#333';

    document.body.appendChild(banner);
    setTimeout(() => {
        banner.remove();
    }, 3000);
}