import { API_BASE } from "./script.js";

const setAddressBtn = document.getElementById('setAddressBtn');
const addressSelect = document.getElementById('addressSelect');
const output = document.getElementById('for-me-output');
const pointsBtn = document.getElementById('points-btn');
const textBtn = document.getElementById('text-btn');

let visningsModus = 'punkter';
let sisteResultat = null;

// Last adresser fra backend
async function lastAdresser() {
    try {
        const response = await fetch(`${API_BASE}/properties`);
        const adresser = await response.json();

        adresser.forEach(a => {
            const option = document.createElement('option');
            option.value = a.address;
            option.textContent = a.label;
            addressSelect.appendChild(option);
        });
    } catch (err) {
        statusText.textContent = 'Kunne ikke laste adresser.';
        console.error(err);
    }
}

lastAdresser();

// Bytt visningsmodus
pointsBtn.addEventListener('click', () => {
    visningsModus = 'punkter';
    if (sisteResultat) visResultat(sisteResultat);
});

textBtn.addEventListener('click', () => {
    visningsModus = 'tekst';
    if (sisteResultat) visResultat(sisteResultat);
});

// Analyser valgt adresse
setAddressBtn.addEventListener('click', async () => {
    const adresse = addressSelect.value;

    if (!adresse) {
        statusText.textContent = 'Velg en adresse først.';
        return;
    }

    statusText.textContent = 'Analyserer — vennligst vent...';
    output.innerHTML = '';
    setAddressBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/for-meg`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ address })
        });

        const data = await response.json();

        if (!response.ok || data.error) {
            statusText.textContent = data.error || 'Noe gikk galt.';
            return;
        }

        sisteResultat = data;
        visResultat(data);
        statusText.textContent = '';

    } catch (err) {
        statusText.textContent = 'Kunne ikke koble til serveren.';
        console.error(err);
    } finally {
        setAddressBtn.disabled = false;
    }
});

function visResultat(data) {
    output.innerHTML = '';

    if (visningsModus === 'tekst') {
        const li = document.createElement('li');
        li.textContent = data.sammendrag;
        output.appendChild(li);
    } else {
        data.punkter.forEach(punkt => {
            const li = document.createElement('li');
            const farge = punkt.type === 'positiv' ? 'green'
                        : punkt.type === 'negativ' ? 'red'
                        : 'gray';
            li.innerHTML = `
                <span style="color:${farge}">●</span>
                <strong>${punkt.tittel}</strong><br>
                ${punkt.beskrivelse}
            `;
            output.appendChild(li);
        });
    }
}