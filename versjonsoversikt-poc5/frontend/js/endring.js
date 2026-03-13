import { API_BASE } from "./script.js";

//hente analyse for alle endringer
window.onload = async function () {
    const changesOutput = document.getElementById('all-changes-output');
    if (!changesOutput) return;

    try {
        const response = await fetch(`${API_BASE}/all-changes-analysis`);

        if (!response.ok) {
            const errorText = await response.text();
            changesOutput.innerHTML = `<p class="error">${errorText}</p>`;
            return;
        }

        const data = await response.json();

        if (data.error) {
            changesOutput.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }

        const versjoner = data.dokumentversjoner;

        if (!versjoner || versjoner.length === 0) {
            changesOutput.innerHTML = '<p class="error">Ingen endringer funnet</p>';
            return;
        }

        let html = '';
        versjoner.forEach(versjon => {
            html += `<h2>${versjon.dato} — ${versjon.filnavn}</h2>`;
            if (versjon.endringer_fra_forrige && versjon.endringer_fra_forrige.length > 0) {
                html += '<ul>';
                versjon.endringer_fra_forrige.forEach(endring => {
                    html += `<li>${endring}</li>`;
                });
                html += '</ul>';
            } else {
                html += '<p>Ingen endringer fra forrige versjon</p>';
            }
        });

        changesOutput.innerHTML = html;

    } catch (error) {
        console.error('Backend feil:', error);
        changesOutput.innerHTML = '<p class="error">Kunne ikke hente analyse. Sjekk at backend kjører.</p>';
    }
};