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
        const files = document.getElementById('planbestemmelse').files;

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
//hent analyse
window.onload = async function () {
    try{
        const response = await fetch(`${API_BASE}/analysis`);
        const data = await response.json();

        const lawOutput = document.getElementById('law-output');
        const currentLaw = document.getElementById('current-law');

        if (!response.ok) {
            summaryOutput.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }

        const lawInformation = data.law_information || {};  
    
        
        // Lover (klikkbare)
            let html = `<h3>Lover</h3><ul class="law-buttons">`;
            html += `<li><button type="button" class="law-item" </button></li>`;
            for (const law of data.auto_laws.laws) {
                html += `<li><button type="button" class="law-item" data-law="${law.name}">${law.name} </button></li>`;
            }
            html += `</ul>`;

        lawOutput.innerHTML = html;

        const lawButtons = lawOutput.querySelectorAll('.law-item');
        lawButtons.forEach(button => {
            button.addEventListener('click', () => {
                const name = button.getAttribute('data-law');
                showSummary(name);
            });
        });

    } catch (error) {
        console.error("Backend feil:", error);
        document.getElementById('summary-output').innerHTML =
            `<p class="error">Kunne ikke hente analyse. Sjekk at backend kjører.</p>`;
    }
}
