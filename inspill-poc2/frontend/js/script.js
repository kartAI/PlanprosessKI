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

// Hent dokumenter fra backend - kun på oppsummering.html
async function loadDocuments() {
    try {

        // Bruk no-store for å sikre at vi ikke får cached resultat
        const response = await fetch('http://localhost:5000/documents?t=' + Date.now(), {
            method: 'GET',
            cache: 'no-store'

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

//hent analyse
window.onload = async function () {
    try {
        const response = await fetch(`${API_BASE}/analysis`);
        const data = await response.json();

        const summaryOutput = document.getElementById('summary-output');
        const categoryOutput = document.getElementById('category-output');
        const currentCategory = document.getElementById('current-category');

        if (!response.ok) {
            summaryOutput.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }

        const combinedSummary = data.combined_summary;
        const categorySummaries = data.category_summaries || {};

        function showSummary(categoryName) {
            const isAll = categoryName === 'Alle';
            if (currentCategory) {
                currentCategory.textContent = categoryName;
            }
            const title = isAll ? 'Felles oppsummering' : `Oppsummering - ${categoryName}`;
            const summaryText = isAll ? combinedSummary : (categorySummaries[categoryName] || 'Ingen oppsummering for denne kategorien.');
            summaryOutput.innerHTML = `
                <h3>${title}</h3>
                <p>${summaryText}</p>
            `;
        }

        // Felles oppsummering
        showSummary('Alle');

        // Kategorier (klikkbare)
        let html = `<h3>Kategorier</h3><ul>`;
        html += `<li><button type="button" class="category-item" data-category="Alle">Alle</button></li>`;
        for (const cat of data.auto_categories.kategorier) {
            html += `<li><button type="button" class="category-item" data-category="${cat.navn}">${cat.navn}</button></li>`;
        }
        html += `</ul>`;

        categoryOutput.innerHTML = html;

        const categoryButtons = categoryOutput.querySelectorAll('.category-item');
        categoryButtons.forEach(button => {
            button.addEventListener('click', () => {
                const name = button.getAttribute('data-category');
                showSummary(name);
            });
        });

    } catch (error) {
        console.error("Backend feil:", error);
        document.getElementById('summary-output').innerHTML =
            `<p class="error">Kunne ikke hente analyse. Sjekk at backend kjører.</p>`;
    }
};
