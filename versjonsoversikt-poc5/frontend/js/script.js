/**
 * Laster inn en HTML‑fil og setter den inn i mål‑elementet.
 * @param {string} elementId - ID‑en til mål‑elementet.
 * @param {string} filePath - Stien til HTML‑filen som skal inkluderes.
 */
    function includeHTML(elementId, filePath) {
    fetch(filePath)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to load ${filePath}: ${response.status}`);
            }
            return response.text();
        })
        .then(data => {
            document.getElementById(elementId).innerHTML = data;
        })
        .catch(error => {
            console.error(error);
            document.getElementById(elementId).innerHTML = "<p style='color:red;'>Error loading content.</p>";
        });
    }

// Inkluderer header elementet HTML
includeHTML("header", "header.html");

// Velger riktig backend-base URL for alle maskiner
export const API_BASE =
window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:5000"
    : "http://localhost:5000";








