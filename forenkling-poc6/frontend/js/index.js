import { API_BASE } from "./script.js";

// Håndter skjema-innsending
const uploadForm = document.getElementById('uploadForm');
if (uploadForm) {
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        const files = document.getElementById('planbeskrivelse-fil').files;

        // Valider at én fil er valgt
        if (files.length === 0) {
            showBanner('Vennligst velg minst én fil', 'error');
            return;
        }

        if (files.length > 1) {
            showBanner('Kun ett dokument er tillatt', 'error');
            return;
        }
        
        formData.append("file", files[0]);

        try {
            const response = await fetch(`${API_BASE}/upload`, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                // Ikke-blokkerende melding; redirect umiddelbart
                showBanner('Opplasting fullført — sender til oppsummmering...', 'success');
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

// Hent input og tekstfelt
const fileInput = document.getElementById("planbeskrivelse-fil");
const fileNameDisplay = document.getElementById("forenkling-name");

// Oppdater tekst når bruker velger fil
if (fileInput) {
    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            const names = Array.from(fileInput.files).map(f => f.name).join(', ');
            fileNameDisplay.textContent = names;
        } else {
            fileNameDisplay.textContent = "Ingen fil valgt";
        }
    });
}

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
