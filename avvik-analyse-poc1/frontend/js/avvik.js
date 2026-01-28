// Hent dokumenter når siden laster
window.onload = async function() {
    try {
        // Hent opplastede filer fra backend
        const response = await fetch('http://localhost:5000/file-content');
        if (response.ok) {
            const fileContents = await response.json();
            
            // Populer de tre bokser med opplastet innhold
            const fileArray = Object.entries(fileContents);
            if (fileArray.length > 0) {
                // Vis filnavn i header
                const fileInfo = document.createElement('div');
                fileInfo.style.fontSize = '0.85rem';
                fileInfo.style.color = '#666';
                fileInfo.style.marginTop = '10px';
                fileInfo.innerHTML = fileArray.map(([name]) => `📄 ${name}`).join('<br>');
                document.querySelector('.header').appendChild(fileInfo);
                
                // Fordel filer til de tre boksene (basert på filrekkefølge)
                document.getElementById('plankart-content').innerHTML = `<pre>${fileArray[0]?.[1] || 'Ikke lastet opp'}</pre>`;
                document.getElementById('bestemmelse-content').innerHTML = `<pre>${fileArray[1]?.[1] || 'Ikke lastet opp'}</pre>`;
                document.getElementById('beskrivelse-content').innerHTML = `<pre>${fileArray[2]?.[1] || 'Ikke lastet opp'}</pre>`;
                
                // Vis innhold
                document.getElementById('content').style.display = 'block';
                document.getElementById('no-selection').style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Kunne ikke hente data:', error);
    }
};
