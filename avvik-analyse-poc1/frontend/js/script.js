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
    const planbestemmelse = document.getElementById('planbestemmelse').files[0];
    const planbeskrivelse = document.getElementById('planbeskrivelse').files[0];
    const plankart = document.getElementById('plankart').files[0];
    
    // Sjekk at alle filer er valgt
    if (!planbestemmelse || !planbeskrivelse || !plankart) {
        alert('Vennligst velg alle tre filene før opplasting');
        return;
    }
    
    // Legg til filene i FormData med riktige navn som matcher backend
    formData.append('file1', planbestemmelse);
    formData.append('file2', planbeskrivelse);
    formData.append('file3', plankart);
    
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


