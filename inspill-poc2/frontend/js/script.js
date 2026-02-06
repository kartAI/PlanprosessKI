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
        const files = document.getElementById('innspill').files;

        if (!files || files.length === 0) {
            alert('Vennligst velg minst én fil');
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
                alert('Filene ble lastet opp!');
                window.location.href = 'oppsummering.html';
            } else {
                const error = await response.text();
                alert('Feil ved opplasting: ' + error);
            }
        } catch (error) {
            alert('Kunne ikke koble til serveren. Er Flask-serveren kjørende?');
            console.error('Error:', error);
        }
    });
}

// Hent dokumenter fra backend - kun på oppsummering.html
async function loadDocuments() {
    try {
        const response = await fetch(`${API_BASE}/documents`, {
            method: 'GET'
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

// Kall funksjonen når siden lastes
document.addEventListener('DOMContentLoaded', loadDocuments);

//hent analyse
window.onload = async function () {
    try {
        const response = await fetch(`${API_BASE}/analysis`);
        const data = await response.json();

        const summaryOutput = document.getElementById('summary-output');
        const categoryOutput = document.getElementById('category-output');

        if (!response.ok) {
            summaryOutput.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }

        // Felles oppsummering
        summaryOutput.innerHTML = `
            <h3>Felles oppsummering</h3>
            <p>${data.combined_summary}</p>
        `;

        // Kategorier + oppsummering per kategori
        let html = `<h3>Kategorier</h3><ul>`;
        for (const cat of data.auto_categories.kategorier) {
            html += `<li><strong>${cat.navn}</strong>: ${cat.beskrivelse}</li>`;
        }
        html += `</ul><h3>Oppsummering per kategori</h3>`;

        for (const [name, summary] of Object.entries(data.category_summaries)) {
            html += `<h4>${name}</h4><p>${summary}</p>`;
        }

        categoryOutput.innerHTML = html;

    } catch (error) {
        console.error("Backend feil:", error);
        document.getElementById('summary-output').innerHTML =
            `<p class="error">Kunne ikke hente analyse. Sjekk at backend kjører.</p>`;
    }
};