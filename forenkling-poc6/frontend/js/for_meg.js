import { API_BASE } from "./script.js";

const setAddressBtn = document.getElementById("setAddressBtn");
const addressSelect = document.getElementById("addressSelect");
const statusText = document.getElementById("statusText");
const output = document.getElementById("for-me-output");
const pointsBtn = document.getElementById("points-btn");
const textBtn = document.getElementById("text-btn");
const pdfViewer = document.getElementById("pdfViewer1");

let sisteResultat = null;
let visningsModus = "punkter";

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function visResultat(data) {
    const punkter = Array.isArray(data?.punkter) ? data.punkter : [];
    output.innerHTML = "";

    if (!punkter.length) {
        output.innerHTML = "<li>Ingen punkter funnet i analysen.</li>";
        return;
    }

    if (visningsModus === "tekst") {
        const tekst = punkter
            .map(p => `${p.tittel || "Uten tittel"}: ${p.beskrivelse || ""}`)
            .join(" ");
        output.innerHTML = `<li>${escapeHtml(tekst)}</li>`;
        return;
    }

    punkter.forEach(p => {
        const li = document.createElement("li");
        li.innerHTML = `<strong>${escapeHtml(p.tittel || "Uten tittel")}:</strong> ${escapeHtml(p.beskrivelse || "")}`;
        output.appendChild(li);
    });
}

async function loadAdresser() {
    try {
        const response = await fetch(`${API_BASE}/properties`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const adresser = await response.json();

        adresser.forEach(a => {
            const option = document.createElement("option");
            option.value = a.address;
            option.textContent = a.label;
            addressSelect.appendChild(option);
        });
    } catch (err) {
        statusText.textContent = "Kunne ikke laste adresser.";
        console.error(err);
    }
}

async function loadLatestPdf() {
    try {
        const response = await fetch(`${API_BASE}/latest-upload`);
        if (!response.ok) return;
        const data = await response.json();
        if (data?.filename) {
            pdfViewer.src = `${API_BASE}/uploads/${encodeURIComponent(data.filename)}`;
        }
    } catch (err) {
        console.error("Kunne ikke laste PDF i viewer:", err);
    }
}

loadAdresser();
loadLatestPdf();

pointsBtn.addEventListener("click", () => {
    visningsModus = "punkter";
    if (sisteResultat) visResultat(sisteResultat);
});

textBtn.addEventListener("click", () => {
    visningsModus = "tekst";
    if (sisteResultat) visResultat(sisteResultat);
});

setAddressBtn.addEventListener("click", async () => {
    const adresse = (addressSelect.value || "").trim();

    if (!adresse) {
        statusText.textContent = "Velg en adresse først.";
        return;
    }

    statusText.textContent = "Analyserer — vennligst vent...";
    output.innerHTML = "";
    setAddressBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/for-meg`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ address: adresse })
        });

        const data = await response.json().catch(() => ({ error: "Ugyldig svar fra server" }));

        if (!response.ok || data.error) {
            statusText.textContent = data.error || `Feil ${response.status}`;
            console.error("API Error:", { status: response.status, data });
            return;
        }

        sisteResultat = data;
        visResultat(data);
        statusText.textContent = "";
    } catch (err) {
        statusText.textContent = "Uventet feil i klienten. Se console.";
        console.error(err);
    } finally {
        setAddressBtn.disabled = false;
    }
});