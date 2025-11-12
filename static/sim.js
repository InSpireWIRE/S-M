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
            window.uploadedDeckId = data.deck_id;
            // Show results
            document.getElementById('status-text').innerText = '✅ Processing Complete!';
            document.getElementById('chunk-info').innerHTML = `
                <strong>Results:</strong><br>
                📄 Pages: ${data.stats.pages}<br>
                📝 Characters extracted: ${data.stats.characters}<br>
                🧩 Chunks created: ${data.stats.chunks}<br>
                🎯 Entities found: ${data.stats.entities_found.names} names, ${data.stats.entities_found.locations} locations
            `;
            document.getElementById("start-btn").style.display = "block";
            setTimeout(() => { document.getElementById("processing-status").style.display = "none"; }, 2000);
            
            // Store deck ID
            window.uploadedDeckId = data.deck_id;
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
        }
        );
    }
});

async function startConversation() {
    if (!window.uploadedDeckId) {
        alert('No document uploaded');
        return;
    }
    
    try {
        const response = await fetch('/api/start-conversation', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({deck_id: window.uploadedDeckId})
        });
        
        const data = await response.json();
        
        window.conversationId = data.conversation_id;
        if (data.questions && data.questions.length > 0) {
            // Display the AI question in the conversation area
            const convArea = document.getElementById('conversation-area');
            convArea.innerHTML = `
                <div class="message ai-message">
                    <p>${data.questions[0]}</p>
                </div>
            `;
            
            // Hide the start button
            document.getElementById('start-btn').style.display = 'none';
            
            // Show the message input area
            document.getElementById("message-input").disabled = false;
            document.getElementById("send-btn").disabled = false;
            document.getElementById('message-input').style.display = 'block';
        }
    } catch (error) {
        console.error('Failed to start conversation:', error);
    }
}
window.startConversation = startConversation;
