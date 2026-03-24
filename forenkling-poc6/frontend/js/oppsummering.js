import { API_BASE } from "./script.js";

// Hente oppsummeringsanalyse 
window.onload = async function () {
    // Hent opplastet dokument og vis PDF i viewer.
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

    // Hent analysen
    const summaryOutput = document.getElementById('oppsummering-output');
    if (!summaryOutput) return;
    
    // Spinner mens analysen kjører
    summaryOutput.innerHTML = `
        <div class="spinner-container">
            <div class="spinner"></div>
            <p>Analyserer planbeskrivelse...</p>
        </div>
    `;

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

        // Bygge UI med collapse meny
        let html = '';
        data.punkt.forEach((punkt, index) => {
            html += `
                <div class="punkt-container">
                    <h2 class="punkt-tittel" onclick="toggleUnderpunkter(${index})">
                        ${punkt.tittel} <span class="arrow">▶</span>
                    </h2>
                    <ul class="underpunkter-liste" id="underpunkter-${index}" style="display: none;">
                        ${punkt.underpunkter.map(u => `<li>${u.beskrivelse}</li>`).join('')}
                    </ul>
                </div>
            `;
        });

        summaryOutput.innerHTML = html;
        
    } catch (error) {
        console.error('Backend feil:', error);
        summaryOutput.innerHTML = '<p class="error">Kunne ikke hente analyse. Sjekk at backend kjører.</p>';
    }
};

// Vise underpunkter med toggle funksjon
window.toggleUnderpunkter = function(index) {
    const liste = document.getElementById(`underpunkter-${index}`);
    const arrow = liste.previousElementSibling.querySelector('.arrow');
    
    if (liste.style.display === 'none') {
        liste.style.display = 'block';
        arrow.textContent = '▼';
    } else {
        liste.style.display = 'none';
        arrow.textContent = '▶';
    }
};

// Åpne og lukke alle punktene
window.toggleAll = function() {
    const lister = document.querySelectorAll('.underpunkter-liste');
    const button = document.getElementById('toggle-all');
    const openAll = [...lister].every(l => l.style.display === 'block');

    lister.forEach((liste, index) => {
        const arrow = document.getElementById(`underpunkter-${index}`)
            .previousElementSibling
            .querySelector('.arrow');

        if (openAll) {
            liste.style.display = 'none';
            arrow.textContent = '▶';
        } else {
            liste.style.display = 'block';
            arrow.textContent = '▼';
        }
    });

    button.textContent = openAll ? 'Åpne alle' : 'Lukk alle';
};