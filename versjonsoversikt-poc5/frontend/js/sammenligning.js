import { API_BASE } from "./script.js";

//Henter dokumentene fra uplods og legger dem i dropdown menyene for sammenligning
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

    function updateView() {
        viewer1.src = select1.value ? `${API_BASE}/uploads/${encodeURIComponent(select1.value)}` : "";
        viewer2.src = select2.value ? `${API_BASE}/uploads/${encodeURIComponent(select2.value)}` : "";
    }

    select1.addEventListener("change", updateView);
    select2.addEventListener("change", updateView);
    updateView();
}

document.addEventListener("DOMContentLoaded", () => {
    loadDocumentsForComparison();
    setupComparisonView();
});