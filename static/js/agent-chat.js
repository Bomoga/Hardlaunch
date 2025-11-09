const script = document.currentScript;
const agentType = script.getAttribute('data-agent-type');

window.sessionId = window.sessionId || localStorage.getItem('hardlaunch_session_id');
let conversationHistory = [];

const summary = localStorage.getItem('business_summary');
if (!summary) {
    const responseBox = document.getElementById('responseBox');
    if (responseBox) {
        responseBox.innerHTML = `
            <div style="text-align: center; padding: 3rem;">
                <h2 style="color: #f85149; margin-bottom: 1rem;">⚠️ Business Summary Required</h2>
                <p style="color: #c9d1d9; margin-bottom: 1rem; line-height: 1.6;">
                    You need to complete the initial business survey before you can chat with specialized agents.
                </p>
                <p style="color: #8b949e; margin-bottom: 2rem;">
                    The survey helps our AI agents understand your startup and provide personalized guidance.
                </p>
                <a href="/static/index.html" style="padding: 1rem 2rem; background: linear-gradient(135deg, #4c8dd6, #2d5fa3); color: white; text-decoration: none; border-radius: 8px; display: inline-block; font-size: 1.1rem;">
                    Complete Survey Now →
                </a>
            </div>
        `;
    }
    
    const input = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    if (input) input.disabled = true;
    if (sendButton) sendButton.disabled = true;
    
    throw new Error('Business summary required');
}

async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    const sendButton = document.getElementById('sendButton');
    
    sendButton.disabled = true;
    sendButton.textContent = 'Sending...';
    
    addMessageToHistory('user', message, false);
    addMessageToHistory('assistant', 'Thinking...', false);
    
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
        
        conversationHistory.pop();
        addMessageToHistory('assistant', data.response, true);
        
        if (data.summary) {
            localStorage.setItem('business_summary', JSON.stringify(data.summary));
        }
        
        input.value = '';
        
    } catch (error) {
        conversationHistory.pop();
        addMessageToHistory('assistant', `Error: ${error.message}`, false);
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
