const API_BASE = '/api';
let sessionId = localStorage.getItem('hardlaunch_session_id');

async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    const sendButton = document.getElementById('sendButton');
    const responseContent = document.getElementById('responseContent');
    const placeholder = document.querySelector('.placeholder');
    
    sendButton.disabled = true;
    sendButton.textContent = 'Sending...';
    
    if (placeholder) {
        placeholder.style.display = 'none';
    }
    
    responseContent.innerHTML = '<p style="color: #6e7681;">Thinking...</p>';
    
    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message
            })
        });
        
        const data = await response.json();
        
        if (data.session_id && !sessionId) {
            sessionId = data.session_id;
            localStorage.setItem('hardlaunch_session_id', sessionId);
        }
        
        responseContent.innerHTML = `
            <p style="margin-bottom: 1rem;"><strong>You:</strong> ${message}</p>
            <p><strong>HardLaunch:</strong> ${data.response}</p>
        `;
        
        if (data.summary) {
            localStorage.setItem('business_summary', JSON.stringify(data.summary));
        }
        
        input.value = '';
        
    } catch (error) {
        responseContent.innerHTML = `<p style="color: #f85149;">Error: ${error.message}</p>`;
    } finally {
        sendButton.disabled = false;
        sendButton.textContent = 'Send';
    }
}

if (document.getElementById('sendButton')) {
    document.getElementById('sendButton').addEventListener('click', sendMessage);
    
    document.getElementById('userInput').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}
