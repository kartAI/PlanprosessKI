import { API_BASE } from "./script.js";

//hente analyse for alle endringer
window.onload = async function () {
    // Hent opplastet dokument og vis første PDF i viewer.
    try {
        const docRes = await fetch(`${API_BASE}/documents`);
        if (!docRes.ok) throw new Error('Kunne ikke hente dokumentliste');

        const docList = await docRes.json();
        if (docList.length > 0) {
            const pdfViewer = document.getElementById('pdfViewer');
            if (pdfViewer) {
                pdfViewer.src = `${API_BASE}/uploads/${encodeURIComponent(docList[0])}`;
            }
        }
    } catch (error) {
        console.error('Kunne ikke hente dokument:', error);
    }

    const summaryOutput = document.getElementById('oppsummering-output');
    if (!summaryOutput) return;

    try {
        const response = await fetch(`${API_BASE}/summary-analysis`);

        if (!response.ok) {
            const errorText = await response.text();
            summaryOutput.innerHTML = `<p class="error">${errorText}</p>`;
            return;
        }

        const data = await response.json();

        if (data.error) {
            summaryOutput.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }

        let html = '';
        data.punkt.forEach(punkt => {
            html += `<h2>${punkt.tittel}</h2>`;
            html += '<ul>';
            punkt.underpunkter.forEach(underpunkt => {
                html += `<li>${underpunkt.beskrivelse}</li>`;
            });
            html += '</ul>';
        });

        summaryOutput.innerHTML = html;
        

    } catch (error) {
        console.error('Backend feil:', error);
        summaryOutput.innerHTML = '<p class="error">Kunne ikke hente analyse. Sjekk at backend kjører.</p>';
    }
};