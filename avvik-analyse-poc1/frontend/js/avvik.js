function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function parseComparisonOutput(text) {
    const lines = text.split('\n');
    let html = '';
    let inTable = false;
    let tableLines = [];
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        
        // Detekterer markdown-tabell
        if (line.includes('|')) {
            if (!inTable) {
                inTable = true;
                tableLines = [];
            }
            tableLines.push(line);
        } else {
            // Hvis vi var i tabell, konvertér den nå
            if (inTable && tableLines.length > 0) {
                html += convertMarkdownTable(tableLines);
                tableLines = [];
                inTable = false;
            }
            
            // Håndter oppsummeringsseksjoner
            if (line.startsWith('===')) {
                html += `<h3 class="section-title">${escapeHtml(line)}</h3>`;
            } else if (line.trim().length > 0) {
                html += `<p>${escapeHtml(line)}</p>`;
            }
        }
    }
    
    // Konvertér eventuell gjenværende tabell
    if (inTable && tableLines.length > 0) {
        html += convertMarkdownTable(tableLines);
    }
    
    return html;
}

function convertMarkdownTable(lines) {
    let table = '<table class="comparison-table"><thead><tr>';
    
    // Header
    const headerRow = lines[0].split('|').map(cell => cell.trim()).filter(c => c);
    headerRow.forEach(cell => {
        table += `<th>${escapeHtml(cell)}</th>`;
    });
    table += '</tr></thead><tbody>';
    
    // Data rows (skip separator line)
    for (let i = 2; i < lines.length; i++) {
        const cells = lines[i].split('|').map(cell => cell.trim()).filter(c => c);
        if (cells.length > 0) {
            table += '<tr>';
            cells.forEach(cell => {
                table += `<td>${escapeHtml(cell)}</td>`;
            });
            table += '</tr>';
        }
    }
    
    table += '</tbody></table>';
    return table;
}

// Hent analyse når siden laster
window.onload = async function() {
    try {
        const analysisResponse = await fetch('http://localhost:5000/analysis-results');
        const analysisOutput = document.getElementById('analysis-output');

        if (analysisResponse.ok) {
            const data = await analysisResponse.json();
            const outputText = data.terminal_output || 'Ingen analyse tilgjengelig.';
            analysisOutput.innerHTML = parseComparisonOutput(outputText);
        } else {
            const errorData = await analysisResponse.json().catch(() => ({}));
            const errorText = errorData.error || 'Kunne ikke hente analyse.';
            analysisOutput.innerHTML = `<p class="error">FEIL: ${escapeHtml(errorText)}</p>`;
        }
    } catch (error) {
        console.error('Backend feil:', error);
        const analysisOutput = document.getElementById('analysis-output');
        if (analysisOutput) {
            analysisOutput.innerHTML = `<p class="error">FEIL: Backend kjører ikke på localhost:5000<br>Start den med: python file.py</p>`;
        }
    }
};
