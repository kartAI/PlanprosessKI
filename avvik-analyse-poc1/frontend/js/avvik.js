// Hent dokumenter når siden laster
window.onload = async function() {
    try {
        // Hent opplastede filer fra localStorage
        const uploadedFiles = JSON.parse(localStorage.getItem('uploadedFiles') || '{}');
        
        if (Object.keys(uploadedFiles).length > 0) {
            // Vis filnavn i header
            const fileInfo = document.createElement('div');
            fileInfo.style.fontSize = '0.85rem';
            fileInfo.style.color = '#666';
            fileInfo.style.marginTop = '10px';
            fileInfo.innerHTML = `
                Planbestemmelse: ${uploadedFiles.planbestemmelse || 'Ikke lastet opp'}<br>
                Planbeskrivelse: ${uploadedFiles.planbeskrivelse || 'Ikke lastet opp'}<br>
                Plankart: ${uploadedFiles.plankart || 'Ikke lastet opp'}
            `;
            document.querySelector('.header').appendChild(fileInfo);
            
            // Populer de tre bokser med opplastet innhold
            document.getElementById('plankart-content').innerHTML = uploadedFiles.plankart || '<p style="color: #999;">Ikke lastet opp</p>';
            document.getElementById('bestemmelse-content').innerHTML = uploadedFiles.planbestemmelse || '<p style="color: #999;">Ikke lastet opp</p>';
            document.getElementById('beskrivelse-content').innerHTML = uploadedFiles.planbeskrivelse || '<p style="color: #999;">Ikke lastet opp</p>';
            
            // Vis innhold
            document.getElementById('content').style.display = 'block';
            document.getElementById('no-selection').style.display = 'none';
        }
        
        // Hent avvik fra backend
        const response = await fetch('http://127.0.0.1:5500/avvik-analyse-poc1/frontend/avvik.html');
        if (response.ok) {
            const avvikData = await response.json();
        }
    } catch (error) {
        console.error('Kunne ikke hente data:', error);
    }
};
