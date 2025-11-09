const script = document.currentScript;
const agentType = script.getAttribute('data-agent-type');

window.sessionId = window.sessionId || localStorage.getItem('hardlaunch_session_id');
window.conversationHistory = window.conversationHistory || [];

async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    const sendButton = document.getElementById('sendButton');
    
    sendButton.disabled = true;
    sendButton.textContent = 'Sending...';
    
    if (typeof addMessageToHistory !== 'undefined') {
        addMessageToHistory('user', message, false);
        addMessageToHistory('assistant', 'Thinking...', false);
    }
    
    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: window.sessionId,
                message: message,
                agent_type: agentType
            })
        });
        
        const data = await response.json();
        
        if (data.session_id && !window.sessionId) {
            window.sessionId = data.session_id;
            localStorage.setItem('hardlaunch_session_id', window.sessionId);
        }
        
        if (typeof addMessageToHistory !== 'undefined') {
            window.conversationHistory.pop();
            addMessageToHistory('assistant', data.response, true);
        }
        
        if (data.summary) {
            localStorage.setItem('business_summary', JSON.stringify(data.summary));
        }
        
        input.value = '';
        
    } catch (error) {
        if (typeof addMessageToHistory !== 'undefined') {
            window.conversationHistory.pop();
            addMessageToHistory('assistant', `Error: ${error.message}`, false);
        }
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
