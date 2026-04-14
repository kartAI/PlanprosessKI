import { API_BASE } from "./script.js";

const analyseTextBtn = document.getElementById("analyseTextBtn");
const innspillInput  = document.getElementById("innspillInput");
const statusText     = document.getElementById("statusText");
const output         = document.getElementById("input-output");

function visResultat(data) {
    const tekst = Array.isArray(data?.Tekst) ? data.Tekst : [];
    output.innerHTML = "";

    if (!tekst.length) {
        output.innerHTML = "<li>Ingen forslag funnet i analysen.</li>";
        return;
    }

    tekst.forEach(t => {
        const li = document.createElement("li");
        li.innerHTML = `<strong>${escapeHtml(t.tittel || "Uten tittel")}:</strong> ${escapeHtml(t.beskrivelse || "")}`;
        output.appendChild(li);
    });
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

analyseTextBtn.addEventListener("click", async (e) => {
    e.preventDefault(); // hindrer form-submit fra å laste siden på nytt

    const text = (innspillInput.value || "").trim();

    if (!text) {
        statusText.textContent = "Skriv inn tekst først.";
        return;
    }

    statusText.textContent = "Analyserer — vennligst vent...";
    output.innerHTML = "";
    analyseTextBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/text-analyse`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        const data = await response.json().catch(() => ({ error: "Ugyldig svar fra server" }));
        console.log("Svar fra API:", data);       
        console.log("data.Tekst:", data?.Tekst);   

        if (!response.ok || data.error) {
            statusText.textContent = data.error || `Feil ${response.status}`;
            console.error("API Error:", { status: response.status, data });
            return;
        }

        visResultat(data);
        statusText.textContent = "";
    } catch (err) {
        statusText.textContent = "Uventet feil i klienten. Se console.";
        console.error(err);
    } finally {
        analyseTextBtn.disabled = false;
    }
});