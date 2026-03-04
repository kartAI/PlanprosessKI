//hent analyse
window.onload = async function () {
    try{
        const response = await fetch(`${API_BASE}/analysis`);
        const data = await response.json();

        const lawOutput = document.getElementById('law-output');
        const currentLaw = document.getElementById('current-law');

        if (!response.ok) {
            summaryOutput.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }

        const lawInformation = data.law_information || {};  
    
        
        // Lover (klikkbare)
            let html = `<h3>Lover</h3><ul class="law-buttons">`;
            html += `<li><button type="button" class="law-item" </button></li>`;
            for (const law of data.auto_laws.laws) {
                html += `<li><button type="button" class="law-item" data-law="${law.name}">${law.name} </button></li>`;
            }
            html += `</ul>`;

        lawOutput.innerHTML = html;

        const lawButtons = lawOutput.querySelectorAll('.law-item');
        lawButtons.forEach(button => {
            button.addEventListener('click', () => {
                const name = button.getAttribute('data-law');
                showSummary(name);
            });
        });

    } catch (error) {
        console.error("Backend feil:", error);
        document.getElementById('summary-output').innerHTML =
            `<p class="error">Kunne ikke hente analyse. Sjekk at backend kjører.</p>`;
    }
}
