import { API_BASE } from "./script.js";

// Henter dokumentene fra uploads og legger dem i dropdown menyene for sammenligning
function loadDocumentsForComparison() {
    const select1 = document.getElementById("document1");
    const select2 = document.getElementById("document2");
    if (!select1 || !select2) return;

    select1.innerHTML = '<option value="">Velg dokument</option>';
    select2.innerHTML = '<option value="">Velg dokument</option>';

    fetch(`${API_BASE}/list-uploads`)
        .then(res => res.json())
        .then(files => {
            if (!Array.isArray(files) || files.length === 0) return;

            files.forEach(file => {
                const option1 = document.createElement("option");
                option1.value = file;
                option1.textContent = file;

                const option2 = document.createElement("option");
                option2.value = file;
                option2.textContent = file;

                select1.appendChild(option1);
                select2.appendChild(option2);
            });
        })
        .catch(err => console.error("Feil ved henting av filer:", err));
}

// Oppdaterer PDF-visning når brukeren velger dokumenter for sammenligning
function setupComparisonView() {
    const select1 = document.getElementById("document1");
    const select2 = document.getElementById("document2");
    const viewer1 = document.getElementById("pdfViewer1");
    const viewer2 = document.getElementById("pdfViewer2");

    if (!select1 || !select2 || !viewer1 || !viewer2) return;

    // Oppdaterer visning av valgt pdf
    function updateView() {
        viewer1.src = select1.value ? `${API_BASE}/uploads/${encodeURIComponent(select1.value)}` : "";
        viewer2.src = select2.value ? `${API_BASE}/uploads/${encodeURIComponent(select2.value)}` : "";
    }

    select1.addEventListener("change", updateView);
    select2.addEventListener("change", updateView);
    updateView();
}

// Sender dokumenter til backend
async function submitComparison() {
    const select1 = document.getElementById("document1");
    const select2 = document.getElementById("document2");
    if (!select1.value || !select2.value) { alert("Velg to dokumenter"); return; }

    // Sender filene som Blob til backend
    const [blob1, blob2] = await Promise.all([
        fetch(`${API_BASE}/uploads/${encodeURIComponent(select1.value)}`)
            .then(r => r.blob()),
        fetch(`${API_BASE}/uploads/${encodeURIComponent(select2.value)}`)
            .then(r => r.blob())
    ]);

    const formData = new FormData();

    formData.append("document1", blob1, select1.value);
    formData.append("document2", blob2, select2.value);

    const response = await fetch(`${API_BASE}/compare-versions-analysis`, {
        method: "POST",
        body: formData
    });
    if (!response.ok) throw new Error("Feil ved sammenligning");

    return await response.json();
}

// Vis resultat av sammmenligningsanalysen
function showResult(data) {
    const output = document.getElementById("compare-output");
    if(!output) return;

    output.innerHTML = "";

    // Henter dokumenter
    const versjoner = data?.dokumentversjoner || [];
    if (!versjoner || versjoner.length === 0) {
        output.innerHTML = "<li>Ingen endringer funnet</li>";
        return;
    }

   // Lager et punkt for hver endring
    versjoner.forEach(v => {
        (v.endringer_fra_forrige || []).forEach(endring => {
            const li = document.createElement("li");
            li.textContent = endring;
            output.appendChild(li);
        });
    });
}

// Håndter hva som skjer når analysen starter
async function handleCompareClick() {
    const output = document.getElementById("compare-output");
    if (output) output.innerHTML = "<li>Analyserer dokumentene...</li>";

    // Henter analysen fra backend og viser resultatet i UI
    try {
        const result = await submitComparison();
        showResult(result);
    } catch (err) {
        if (output) output.innerHTML = `<li>${err.message}</li>`;
    }
}

// Laster siden 
window.onload = function () {
    loadDocumentsForComparison();
    setupComparisonView();

    const btn = document.getElementById("compare-btn");
    if (btn) 
        btn.addEventListener("click", handleCompareClick);
};