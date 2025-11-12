// S!M Status Polling System
let pollInterval = null;
let currentDeckId = null;

function startStatusPolling(deckId) {
    currentDeckId = deckId;
    console.log('Starting status polling for deck:', deckId);
    
    pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/status?deck_id=${deckId}`);
            const data = await response.json();
            
            if (data.status === 'processing') {
                updateStatus(`Processing page ${data.current_page} of ${data.total_pages}...`);
            } else if (data.status === 'complete') {
                updateStatus('Processing complete! Starting conversation...');
                stopPolling();
            }
        } catch (error) {
            console.error('Status poll error:', error);
        }
    }, 1000); // Poll every second
}

function stopPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

function updateStatus(message) {
    const statusDiv = document.getElementById('status-message');
    if (statusDiv) {
        statusDiv.innerText = message;
    }
    console.log('Status:', message);
}
