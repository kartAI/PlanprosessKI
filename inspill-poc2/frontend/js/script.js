 const fileInputs = document.querySelectorAll('input[type="file"]');
fileInputs.forEach(input => {
    input.addEventListener('change', function(e) {
        const files = e.target.files;
        const nameElement = document.getElementById(e.target.id + '-name');
        if (!files || files.length === 0) {
            nameElement.textContent = 'Ingen fil valgt';
            nameElement.style.color = '#999';
        } else if (files.length === 1) {
            nameElement.textContent = files[0].name;
            nameElement.style.color = '#667eea';
        } else {
            nameElement.textContent = files.length + ' filer valgt';
            nameElement.style.color = '#667eea';
        }
    });
});

// Håndter skjema-innsending
const uploadForm = document.getElementById('uploadForm');
uploadForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData();
    const files = document.getElementById('innspill').files;

    // Sjekk at minst én fil er valgt
    if (!files || files.length === 0) {
        alert('Vennligst velg minst én fil');
        return;
    }

    // Legg alle filer i FormData med navn 'files' slik backend forventer
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    try {
        const response = await fetch('http://localhost:5000/upload', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            alert('Filene ble lastet opp!');
            window.location.href = 'avvik.html';
        } else {
            const error = await response.text();
            alert('Feil ved opplasting: ' + error);
        }
    } catch (error) {
        alert('Kunne ikke koble til serveren. Er Flask-serveren kjørende?');
        console.error('Error:', error);
    }
});