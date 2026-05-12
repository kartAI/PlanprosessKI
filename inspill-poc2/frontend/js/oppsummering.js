import { API_BASE } from "./script.js";

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

// Hent analyse
window.onload = async function () {
    const summaryOutput = document.getElementById('summary-output');

     // Vis spinner mens analysen kjører
    summaryOutput.innerHTML = `
        <div class="spinner-container">
            <div class="spinner"></div>
            <p>Analyserer høringsinnspill...</p>
        </div>
    `;

    try {
        const response = await fetch(`${API_BASE}/analysis`);
        const data = await response.json();

        const categoryOutput = document.getElementById('category-output');
        const currentCategory = document.getElementById('current-category');
        const documentsList = document.getElementById('documents-list');

        if (!response.ok) {
            summaryOutput.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }

        const combinedSummary = data.combined_summary;
        const categorySummaries = data.category_summaries || {};
        const categoryDocuments = data.category_documents || {};
        const allDocuments = (data.documents || []).map(doc => doc.filename);

        function renderDocuments(files) {
            if (!documentsList) {
                return;
            }
            if (!files || files.length === 0) {
                documentsList.innerHTML = '<p>Ingen dokumenter funnet for denne kategorien.</p>';
                return;
            }
            documentsList.innerHTML = files.map(doc =>
                `<a href="${API_BASE}/uploads/${doc}" target="_blank" class="document-link">${doc}</a>`
            ).join('<br>');
        }

        function showSummary(categoryName) {
            const isAll = categoryName === 'Alle';
            if (currentCategory) {
                currentCategory.textContent = categoryName;
            }
            const title = isAll ? 'Felles oppsummering' : `Oppsummering - ${categoryName}`;
            const summaryText = isAll ? combinedSummary : (categorySummaries[categoryName] || 'Ingen oppsummering for denne kategorien.');
            
            const formatted = summaryText
                .split('\n')                  // del opp på linjeskift
                .map(line => line.trim())
                .filter(line => line)         // fjern tomme linjer
                .map(line => `<p>${line}</p>`) // pakk hver linje i <p>
                .join('');
            
            summaryOutput.innerHTML = `
                <h3>${title}</h3>
                <div class="summary-text">${formatted}</div>
            `;

            const files = isAll ? allDocuments : (categoryDocuments[categoryName] || []);
            renderDocuments(files);
        }

        // Felles oppsummering
        showSummary('Alle');

        // Kategorier (klikkbare)
            let html = `<h3>Kategorier</h3><ul class="category-buttons">`;
            html += `<li><button type="button" class="category-item" data-category="Alle">Alle (${allDocuments.length})</button></li>`;
            for (const cat of data.auto_categories.kategorier) {
                const count = (categoryDocuments[cat.navn] || []).length;
                html += `<li><button type="button" class="category-item" data-category="${cat.navn}">${cat.navn} (${count})</button></li>`;
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
}
