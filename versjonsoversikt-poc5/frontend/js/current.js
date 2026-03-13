import { API_BASE } from "./script.js";

//skriver ut analysen i punktliste på gjelder.html
function loadAnalysis() {
    fetch(`${API_BASE}/current_analysis`)
        .then(res => res.json())
        .then(data => {
            console.log("KI-output:", data);
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

// Kjør analysen når gjelder.html lastes
window.onload = function() {
    loadAnalysis();
};