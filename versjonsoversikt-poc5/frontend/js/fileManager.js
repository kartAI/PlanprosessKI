import { API_BASE } from "./script.js";

// Felles banner-melding
export function showBanner(message, type = 'info') {
    const existing = document.getElementById('upload-banner');
    if (existing) existing.remove();

    const banner = document.createElement('div');
    banner.id = 'upload-banner';
    banner.className = 'upload-banner upload-banner--' + (type || 'info');
    banner.textContent = message;

    document.body.appendChild(banner);
    setTimeout(() => {
        banner.style.opacity = '0';
        banner.style.transform = 'translateX(-50%) translateY(-6px)';
        setTimeout(() => banner.remove(), 250);
    }, 3000);
}

// Generisk filhåndtering
export async function setupFileUpload(formId, inputId, nameDisplayId, uploadEndpoint, callback) {
    const form = document.getElementById(formId);
    const input = document.getElementById(inputId);
    const display = document.getElementById(nameDisplayId);

    if (!form) return;

    // Oppdater filnavn når bruker velger
    if (input) {
        input.addEventListener("change", () => {
            if (input.files.length > 0) {
                const names = Array.from(input.files).map(f => f.name).join(', ');
                display.textContent = names;
            } else {
                display.textContent = "Ingen fil valgt";
            }
        });
    }

    // Håndter innsending
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const files = input.files;
        if (!files || files.length === 0) {
            showBanner('Vennligst velg minst én fil', 'error');
            return;
        }

        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }

        try {
            const response = await fetch(`${API_BASE}${uploadEndpoint}`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                showBanner('Opplasting fullført', 'success');
                input.value = '';
                display.textContent = 'Ingen fil valgt';
                if (callback) callback();
            } else {
                const error = await response.text();
                showBanner('Feil ved opplasting: ' + error, 'error');
            }
        } catch (error) {
            showBanner('Kunne ikke koble til serveren', 'error');
            console.error('Upload error:', error);
        }
    });
}

// Generisk fillistevisning
export function loadFiles(endpoint, containerId, fileBaseUrl, deleteEndpoint, onDelete) {
    fetch(`${API_BASE}${endpoint}`)
        .then(res => res.json())
        .then(files => {
            const container = document.getElementById(containerId);
            if (!container) return;

            container.innerHTML = "";

            if (files.length === 0) {
                container.innerHTML = "<p>Ingen filer er lastet opp enda</p>";
                return;
            }

            files.forEach(file => {
                const div = document.createElement("div");
                div.className = "file-item";

                const link = document.createElement("a");
                link.href = `${API_BASE}${fileBaseUrl}${file}`;
                link.target = "_blank";
                link.textContent = file;
                link.className = "file-link";

                const deleteBtn = document.createElement("button");
                deleteBtn.textContent = "Slett";
                deleteBtn.className = "delete-btn";
                deleteBtn.onclick = () => deleteFile(deleteEndpoint, file, () => {
                    loadFiles(endpoint, containerId, fileBaseUrl, deleteEndpoint, onDelete);
                    if (onDelete) onDelete();
                });

                div.appendChild(link);
                div.appendChild(deleteBtn);
                container.appendChild(div);
            });
        })
        .catch(err => console.error("Feil ved henting av filer:", err));
}

// Generisk filsletting
export function deleteFile(endpoint, filename, callback) {
    if (confirm(`Er du sikker på at du vil slette ${filename}?`)) {
        fetch(`${API_BASE}${endpoint}${filename}`, {
            method: 'DELETE'
        })
        .then(res => res.json())
        .then(data => {
            if (data.message) {
                showBanner('Fil slettet', 'success');
                if (callback) callback();
            } else {
                showBanner('Feil ved sletting: ' + data.error, 'error');
            }
        })
        .catch(err => {
            showBanner('Feil ved sletting', 'error');
            console.error('Delete error:', err);
        });
    }
}