const API_BASE = '/api';
window.sessionId = localStorage.getItem('hardlaunch_session_id');

function parseMarkdown(text) {
    if (!text) return '';
    
    let html = text;
    
    html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
    html = html.replace(/^\* (.+)$/gm, '<li>$1</li>');
    html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    html = html.replace(/<\/ul>\s*<ul>/g, '');
    html = html.replace(/\n\n/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    html = html.replace(/^(.+)$/, '<p>$1</p>');
    
    return html;
}

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
                session_id: window.sessionId,
                message: message
            })
        });
        
        const data = await response.json();
        
        if (data.session_id && !window.sessionId) {
            window.sessionId = data.session_id;
            localStorage.setItem('hardlaunch_session_id', window.sessionId);
        }
        
        const formattedResponse = parseMarkdown(data.response);
        responseContent.innerHTML = `
            <div style="margin-bottom: 1.5rem;">
                <strong style="color: #58a6ff;">You:</strong>
                <div style="margin-top: 0.5rem; padding-left: 1rem; border-left: 3px solid #30363d;">
                    ${message}
                </div>
            </div>
            <div>
                <strong style="color: #58a6ff;">HardLaunch:</strong>
                <div class="markdown-content" style="margin-top: 0.5rem; padding-left: 1rem; border-left: 3px solid #58a6ff;">
                    ${formattedResponse}
                </div>
            </div>
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
