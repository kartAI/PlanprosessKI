import { API_BASE } from "./script.js";

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

        // Legg til én fil i FormData‑objektet.
        formData.append('file', files[0]);  

        const checklistSelect = document.querySelector('select[name="sjekkliste"]');
        const selectedChecklist = checklistSelect ? checklistSelect.value : "";
        if (selectedChecklist) {
            localStorage.setItem("selectedChecklist", selectedChecklist);
            formData.append('sjekkliste', selectedChecklist);
        }

        try {
            const response = await fetch(`${API_BASE}/upload`, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                showBanner('Opplasting fullført — sender til oppsummering...', 'success');
                const nextUrl = selectedChecklist
                    ? `sjekkliste.html?t=${Date.now()}&sjekkliste=${encodeURIComponent(selectedChecklist)}`
                    : `sjekkliste.html?t=${Date.now()}`;
                window.location.href = nextUrl;
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

// Enkel ikke-blokkerende bannermelding
function showBanner(message, type = 'info') {
    const existing = document.getElementById('upload-banner');
    if (existing) existing.remove();

    const banner = document.createElement('div');
    banner.id = 'upload-banner';
    banner.className = 'upload-banner upload-banner--' + (type || 'info');
    banner.textContent = message;

    // fader ut bannered for brukervennlighet
    document.body.appendChild(banner);
    setTimeout(() => {
        banner.style.opacity = '0';
        banner.style.transform = 'translateX(-50%) translateY(-6px)';
        setTimeout(() => banner.remove(), 250);
    }, 3000);
}