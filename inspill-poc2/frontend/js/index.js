import { API_BASE } from "./script.js";

// Oppdater filnavn-label når bruker velger fil(er) i et input[type="file"]-felt.
// Forutsetter at det finnes et element med id "<input-id>-name" for hvert filfelt.
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
        // Fade out for en fin UX
        banner.style.opacity = '0';
        banner.style.transform = 'translateX(-50%) translateY(-6px)';
        setTimeout(() => banner.remove(), 250);
    }, 3000);
}

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
            const response = await fetch(`${API_BASE}/upload`, {
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



// Kall funksjonen når siden lastes
//document.addEventListener('DOMContentLoaded', loadDocuments);