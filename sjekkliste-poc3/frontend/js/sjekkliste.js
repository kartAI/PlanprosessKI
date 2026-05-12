import { API_BASE } from "./script.js";

function getSelectedChecklist() {
    const params = new URLSearchParams(window.location.search);
    const fromQuery = params.get("sjekkliste");
    if (fromQuery) {
        localStorage.setItem("selectedChecklist", fromQuery);
        return fromQuery;
    }
    return localStorage.getItem("selectedChecklist") || "";
}

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

// Hent og vis sjekklisten
async function loadChecklist() {
    try {
        const selectedChecklist = getSelectedChecklist();
        const checklistParam = selectedChecklist
            ? `?name=${encodeURIComponent(selectedChecklist)}`
            : "";
        const response = await fetch(`${API_BASE}/checklist${checklistParam}`);
        const data = await response.json();
        
        const checklistElement = document.getElementById('checklist-list');
        if (checklistElement && data.checklist) {
            checklistElement.innerHTML = data.checklist.map(point => 
                `<li>${point}</li>`
            ).join('');
        }
    } catch (error) {
        console.error('Feil ved henting av sjekkliste:', error);
    }
}

const pdfViewer = document.getElementById("pdfViewer");
if (pdfViewer) {
    fetch(`${API_BASE}/documents`)
        .then(res => res.json())
        .then(files => {
            if (!files || files.length === 0) {
                throw new Error("Ingen opplastet fil funnet");
            }
            const filnavn = files[0]; // alltid én fil
            return fetch(`${API_BASE}/uploads/${filnavn}`);
        })
        .then(response => {
            if (!response.ok) throw new Error("Filen finnes ikke");
            return response.blob();
        })
        .then(blob => {
            // Vis filen
            const url = URL.createObjectURL(blob);
            pdfViewer.src = url;
        })
        .catch(error => {
            // Håndter feil
            alert(error.message);
        });
}

// Hent analysen og vis i frontend
async function loadAnalysis() {
    const analysisList = document.getElementById('analysis-list');
    
    // Vis spinner mens analysen kjører
    analysisList.innerHTML = `
        <div class="spinner-container">
            <div class="spinner"></div>
            <p>Sjekker planbeskrivelse...</p>
        </div>
    `;

    try {
        const selectedChecklist = getSelectedChecklist();
        const analysisParam = selectedChecklist
            ? `?name=${encodeURIComponent(selectedChecklist)}`
            : "";
        const response = await fetch(`${API_BASE}/analysis${analysisParam}`);

        if (!response.ok) {
            const text = await response.text();
            console.error('Analysis request failed:', response.status, text);
            return;
        }

        const data = await response.json();

        if (data.error) {
            console.error('Analysis returned error:', data.error, data.raw);
            return;
        }

        if (!analysisList) {
            console.error('Element #analysis-list ikke funnet');
            return;
        }

        if (!data.resultat || !Array.isArray(data.resultat) || data.resultat.length === 0) {
            analysisList.innerHTML = '<li>Ingen analyse-resultater funnet.</li>';
            return;
        }

        analysisList.innerHTML = data.resultat.map(item => {
            const statusClass = item.status === 'oppfylt' ? 'oppfylt' : 'ikke-oppfylt';
            const statusIcon = item.status === 'oppfylt' ? '✓' : '✗';
            const punkt = item.punkt || 'Ukjent punkt';
            const forklaring = item.forklaring || '';
            return `<li class="analysis-item ${statusClass}">
                <div class="analysis-header">
                    <span class="status-icon">${statusIcon}</span>
                    <span class="punkt">${punkt}</span>
                </div>
                <div class="forklaring">${forklaring}</div>
            </li>`;
        }).join('');
    } catch (error) {
        console.error('Feil ved henting av analyse:', error);
    }
}

// Kaller funksjonen når siden lastes
document.addEventListener('DOMContentLoaded', () => {
    loadChecklist();
    loadAnalysis();
});