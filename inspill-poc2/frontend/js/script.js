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
            const response = await fetch('http://localhost:5000/upload', {
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
        const response = await fetch('http://localhost:5000/documents', {
            method: 'GET'
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

//hent analyse
window.onload = async function () {
    try {
        const response = await fetch('http://localhost:5000/analysis');
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