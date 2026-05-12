import { API_BASE } from "./script.js";
import { setupFileUpload, loadFiles, showBanner } from "./fileManager.js";

// Oppsett for møtereferater
setupFileUpload(
    'uploadForm',
    'versjonsoversikt-fil',
    'versjonsoversikt-navn',
    '/upload-meetings',
    () => {
        loadMeetingsFiles();
        loadAnalysis();
    }
);

// Last møtereferater-filer ved oppstart
function loadMeetingsFiles() {
    loadFiles(
        '/list-meetings',
        'file-list',
        '/meetings/',
        '/delete-meetings/',
        loadAnalysis
    );
}

// Skriver ut analysen
function loadAnalysis() {
        const container = document.getElementById('currentInfo');
        if (!container) return;

        container.innerHTML = `
            <div class="spinner-container">
                <div class="spinner"></div>
                <p>Analyserer...</p>
            </div>
        `;

        fetch(`${API_BASE}/current_analysis`)
            .then(res => res.json())
            .then(data => {
            const container = document.getElementById('currentInfo');
            if (!container) return;
            

            let html = "<ul>";
            try {
                if (data.oppdateringer && Array.isArray(data.oppdateringer) && data.oppdateringer.length > 0) {
                    const latest = data.oppdateringer[0];
                    html += `<h3>${latest.dato}</h3>`;
                    latest.gjeldende.forEach(punkt => {
                        html += `<li><strong>${punkt.tema}:</strong> ${punkt.beskrivelse}</li>`;
                    });
                    html += `</ul>`;
                } else {
                    html += "<p>Ingen gyldige punkter funnet.</p>";
                }
            } catch (e) {
                html += `<p>Feil ved parsing av data.</p>`;
            }
            container.innerHTML = html;
        })
        .catch(err => {
            const container = document.getElementById('currentInfo');
            if (container) container.innerHTML = "<p style='color:red;'>Feil ved henting av analyse.</p>";
            console.error(err);
        });
}

// Kjør når siden lastes
window.onload = function() {
    loadMeetingsFiles();
    loadAnalysis();
};