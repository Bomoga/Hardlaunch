const API_BASE = '/api';
window.sessionId = localStorage.getItem('hardlaunch_session_id');
let conversationHistory = [];

async function checkSubmissionStatus() {
    const sessionId = window.sessionId || localStorage.getItem('hardlaunch_session_id');
    if (!sessionId) {
        return {
            submitted: false,
            hasSummary: false,
            message: 'No session ID found'
        };
    }
    
    try {
        const response = await fetch(`${API_BASE}/submission-status?session_id=${sessionId}`);
        const data = await response.json();
        return {
            submitted: data.submitted || false,
            hasSummary: data.has_summary || false,
            message: data.message || ''
        };
    } catch (error) {
        console.error('Error checking submission status:', error);
        return {
            submitted: false,
            hasSummary: false,
            message: 'Error checking submission status'
        };
    }
}

function parseMarkdown(text) {
    if (!text) return '';
    
    let html = text;
    
    html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$2</h2>');
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

function addMessageToHistory(role, content, isMarkdown = false) {
    conversationHistory.push({ role, content, isMarkdown });
    renderConversation();
}

function renderConversation() {
    const responseContent = document.getElementById('responseContent');
    const placeholder = document.querySelector('.placeholder');
    
    if (placeholder && conversationHistory.length > 0) {
        placeholder.style.display = 'none';
    }
    
    let html = '';
    conversationHistory.forEach(msg => {
        const displayContent = msg.isMarkdown ? parseMarkdown(msg.content) : msg.content;
        const borderColor = msg.role === 'user' ? '#30363d' : '#58a6ff';
        const roleLabel = msg.role === 'user' ? 'You' : 'HardLaunch';
        const roleColor = msg.role === 'user' ? '#8b949e' : '#58a6ff';
        
        html += `
            <div style="margin-bottom: 1.5rem;">
                <strong style="color: ${roleColor};">${roleLabel}:</strong>
                <div class="${msg.isMarkdown ? 'markdown-content' : ''}" style="margin-top: 0.5rem; padding-left: 1rem; border-left: 3px solid ${borderColor};">
                    ${displayContent}
                </div>
            </div>
        `;
    });
    
    responseContent.innerHTML = html;
    
    const responseBox = document.getElementById('responseBox');
    if (responseBox) {
        responseBox.scrollTop = responseBox.scrollHeight;
    }
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
                message: message
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
            
            const continueButton = document.createElement('div');
            continueButton.style.cssText = 'text-align: center; margin-top: 2rem;';
            continueButton.innerHTML = `
                <button onclick="submitAndContinue()" 
                    style="padding: 1rem 2rem; background: linear-gradient(135deg, #4c8dd6, #2d5fa3); color: white; border: none; border-radius: 8px; font-size: 1.1rem; cursor: pointer; box-shadow: 0 4px 12px rgba(76, 141, 214, 0.4); transition: transform 0.2s;">
                    Submit & Continue to Dashboard →
                </button>
            `;
            
            const responseBox = document.getElementById('responseBox');
            if (responseBox && !document.getElementById('continueBtn')) {
                continueButton.id = 'continueBtn';
                responseBox.appendChild(continueButton);
            }
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

async function submitAndContinue() {
    const button = event.target;
    button.disabled = true;
    button.textContent = 'Submitting...';
    
    try {
        const response = await fetch(`${API_BASE}/submit-summary`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: window.sessionId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.location.href = '/';
        } else {
            alert('Error submitting summary: ' + data.message);
            button.disabled = false;
            button.textContent = 'Submit & Continue to Dashboard →';
        }
    } catch (error) {
        alert('Error: ' + error.message);
        button.disabled = false;
        button.textContent = 'Submit & Continue to Dashboard →';
    }
}

// Only add event listeners if agent-chat.js is not loaded (to avoid duplicate submissions on agent pages)
if (document.getElementById('sendButton') && !document.querySelector('script[data-agent-type]')) {
    document.getElementById('sendButton').addEventListener('click', sendMessage);
    
    document.getElementById('userInput').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}
