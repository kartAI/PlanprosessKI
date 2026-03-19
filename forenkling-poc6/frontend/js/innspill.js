import { API_BASE } from "./script.js";

const analyseTextBtn = document.getElementById("analyseTextBtn");
const textSelect = document.getElementById("textSelect");
const statusText = document.getElementById("statusText");
const output = document.getElementById("input-output");

analyseTextBtn.addEventListener("click", async () => {
    const adresse = (textSelect.value || "").trim();

    if (!text) {
        statusText.textContent = "Skriv in tekst.";
        return;
    }

    statusText.textContent = "Analyserer — vennligst vent...";
    output.innerHTML = "";
    setAddressBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/text-analyse`, {
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
        analyseTextBtn.disabled = false;
    }
});