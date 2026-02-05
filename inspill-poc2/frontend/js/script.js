const fileInputs = document.querySelectorAll('input[type="file"]');
fileInputs.forEach(input => {
    input.addEventListener('change', function(e) {
        const fileName = e.target.files[0]?.name || 'Ingen fil valgt';
        const nameElement = document.getElementById(e.target.id + '-name');
        nameElement.textContent = fileName;
        nameElement.style.color = e.target.files[0] ? '#667eea' : '#999';
    });
});


// Håndter skjema-innsending
const uploadForm = document.getElementById('uploadForm');
uploadForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData();
    const innspill = document.getElementById('innspill').files;
    
    // Sjekk at alle filer er valgt
    if (!innspill) {
        alert('Vennligst velg en fil');
        return;
    }
    
    // Legg alle filer i FormData med navn som matcher backend
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


