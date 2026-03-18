/* Laster inn en HTML‑fil og setter den inn i mål‑elementet.
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

// Inkluderer header elementet
includeHTML("header", "header.html");