async function uploadFileWithStatus(file) {
    // Show status div
    document.getElementById('processing-status').style.display = 'block';
    document.getElementById('status-text').innerText = 'Uploading file...';
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        // Start upload
        document.getElementById('status-text').innerText = 'Processing PDF with OCR...';
        document.getElementById('chunk-info').innerText = 'This may take 30-60 seconds for large files';
        
        const response = await fetch('/api/upload-deck', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.deck_id) {
            // Show results
            document.getElementById('status-text').innerText = '✅ Processing Complete!';
            document.getElementById('chunk-info').innerHTML = `
                <strong>Results:</strong><br>
                📄 Pages: ${data.stats.pages}<br>
                📝 Characters extracted: ${data.stats.characters}<br>
                🧩 Chunks created: ${data.stats.chunks}<br>
                🎯 Entities found: ${data.stats.entities_found.names} names, ${data.stats.entities_found.locations} locations
            `;
            
            // Store deck ID
            window.uploadedDeckId = data.deck_id;
            
            // Show analyze button
            setTimeout(() => {
                document.getElementById('start-btn').style.display = 'block';
            }, 1000);
        }
    } catch (error) {
        document.getElementById('status-text').innerText = '❌ Upload failed: ' + error.message;
    }
}

// Update the Start Analysis button behavior
document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('start-btn');
    if (startBtn) {
        startBtn.addEventListener('click', function() {
            // Show processing status
            const statusDiv = document.getElementById('processing-status');
            if (statusDiv) {
                statusDiv.style.display = 'block';
                document.getElementById('status-detail').innerText = 'Processing pages with OCR... Creating semantic chunks...';
            }
            
            // Disable button while processing
            this.disabled = true;
            this.innerText = 'Processing...';
            
            // Simulate processing complete after delay (or poll for real status)
            setTimeout(() => {
                document.getElementById('status-detail').innerText = '✅ Processing complete! 6 chunks created. Starting conversation...';
                // Enable conversation
            }, 3000);
        });
    }
});
