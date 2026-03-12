import { API_BASE } from "./script.js";

function loadAnalysis() {
    fetch(`${API_BASE}/current_analysis`)
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('currentInfo');
            if (!container) return;

            let html = "<ul>";
            try {
                const points = typeof data === "string" ? JSON.parse(data) : data;
                if (Array.isArray(points)) {
                    points.forEach(punkt => html += `<li>${punkt}</li>`);
                } else if (points.result) {
                    points.result.forEach(punkt => html += `<li>${punkt}</li>`);
                } else {
                    html += `<li>${JSON.stringify(points)}</li>`;
                }
            } catch (e) {
                html += `<li>${data}</li>`;
            }
            html += "</ul>";
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