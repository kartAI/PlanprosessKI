// Velger riktig backend-base URL for alle maskiner
const API_BASE =
    window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:5000"
        : "http://localhost:5000";
        
// Viser statusmeldinger i UI (eller i konsollen hvis elementet ikke finnes).
function showBanner(message, type = 'info') {
    const summaryOutput = document.getElementById('summary-output');
    if (summaryOutput) {
        const className = type === 'error' ? 'error' : 'success';
        summaryOutput.innerHTML = `<p class="${className}">${message}</p>`;
        return;
    }
    if (type === 'error') {
        console.error(message);
    } else {
        console.log(message);
    }
}

// Hent alle fil-inputs på siden
const fileInputs = document.querySelectorAll('input[type="file"]');
fileInputs.forEach(input => {
    input.addEventListener('change', function (e) {
        const files = e.target.files;
        const nameElement = document.getElementById(e.target.id + '-name');

        if (!files || files.length === 0) {
            nameElement.textContent = 'Ingen fil valgt';
            nameElement.style.color = '#999';
        } else if (files.length === 1) {
            nameElement.textContent = files[0].name;
            nameElement.style.color = '#667eea';
        } else {
            nameElement.textContent = 'Kun ett dokument er tillatt';
            nameElement.style.color = '#e74c3c';
            e.target.value = '';
        }
    });
});

// Håndter skjema-innsending
const uploadForm = document.getElementById('uploadForm');
if (uploadForm) {
    uploadForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const formData = new FormData();
        const files = document.getElementById('planbestemmelse').files;

        // Valider at én fil er valgt
        if (files.length === 0) {
            showBanner('Vennligst velg minst én fil', 'error');
            return;
        }

        if (files.length > 1) {
            showBanner('Kun ett dokument er tillatt', 'error');
            return;
        }

        formData.append('files', files[0]);

        try {
            const response = await fetch(`${API_BASE}/upload`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                showBanner('Opplasting fullført — sender til lovAnalyse...', 'success');

                const hasChecklist = typeof selectedChecklist !== 'undefined' && selectedChecklist;
                const nextUrl = hasChecklist
                    ? `lovAnalyse.html?t=${Date.now()}&lovAnalyse=${encodeURIComponent(selectedChecklist)}`
                    : `lovAnalyse.html?t=${Date.now()}`;

                window.location.href = nextUrl;
            } else {
                const error = await response.text();
                showBanner('Feil ved opplasting: ' + error, 'error');
                console.error('Uploads error:', error);
            }
        } catch (error) {
            showBanner('Kunne ikke koble til serveren. Er Flask-serveren kjørende?', 'error');
            console.error('Error:', error);
        }
    });
}

// Hent analyse
window.onload = async function () {
    // Hent opplastede dokumenter og vis første PDF
    try {
        const docRes = await fetch(`${API_BASE}/documents`);
        if (!docRes.ok) throw new Error("Kunne ikke hente dokumentliste");

        const docList = await docRes.json();
        if (docList.length > 0) {
            const pdfViewer = document.getElementById('pdfViewer');
            if (pdfViewer) {
                pdfViewer.src = `${API_BASE}/uploads/${encodeURIComponent(docList[0])}`;
            }
        }
    } catch (error) {
        console.error("Kunne ikke hente dokument:", error);
    }

    const lawOutput = document.getElementById('law-output');
    const summaryOutput = document.getElementById('summary-output');

    // Hent analyse fra backend
    try {
        const response = await fetch(`${API_BASE}/analysis`);

        if (!response.ok) {
            const errorText = await response.text();
            if (summaryOutput) {
                summaryOutput.innerHTML = `<p class="error">${errorText}</p>`;
            }
            return;
        }

        const data = await response.json();

        // hent ut filtered-liste (eller bruk hele data hvis du returnerer bare lista)
        const filtered = data.filtered || data;

        const lawOutput = document.getElementById('law-output');
        if (!lawOutput) return;

        if (Array.isArray(filtered) && filtered.length > 0) {
            let html = '<h3>Funnet paragrafer</h3><ul class="law-buttons">';
            filtered.forEach(item => {
                html += `<li>
                    <strong>${item.navn}</strong> ${item.paragraf}<br>
                    ${item.tekst}
                </li>`;
            });
            html += '</ul>';
            lawOutput.innerHTML = html;
        } else {
            lawOutput.innerHTML = '<p class="error">Ingen matchende data funnet</p>';
        }
        
        // Legger til klikk-event for hver lov
        /*const lawButtons = lawOutput.querySelectorAll('.law-item');
        lawButtons.forEach(button => {
            button.addEventListener('click', () => {
                const name = button.getAttribute('data-law');
                showSummary(name);
            });
        });
        */

    } catch (error) {
        console.error("Backend feil:", error);
        lawOutput.innerHTML =
            `<p class="error">Kunne ikke hente analyse. Sjekk at backend kjører.</p>`;
    }
};