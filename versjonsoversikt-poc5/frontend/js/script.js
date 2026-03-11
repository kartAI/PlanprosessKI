
/**
 * Loads an HTML file and inserts it into the target element.
 * @param {string} elementId - The ID of the target element.
 * @param {string} filePath - Path to the HTML file to include.
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

// Include header and footer
includeHTML("header", "header.html");
