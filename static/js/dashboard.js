const summary = localStorage.getItem('business_summary');
if (summary) {
    const summaryData = JSON.parse(summary);
    const summaryElement = document.getElementById('businessSummary');
    if (summaryElement) {
        summaryElement.innerHTML = `
            <div style="margin-top: 1rem; padding: 1rem; background: rgba(88, 166, 255, 0.1); border-radius: 8px;">
                <pre style="white-space: pre-wrap; color: #c9d1d9;">${JSON.stringify(summaryData, null, 2)}</pre>
            </div>
        `;
    }
}

function revertToSurvey() {
    if (confirm('Are you sure you want to restart the survey? This will clear your current session.')) {
        localStorage.removeItem('hardlaunch_session_id');
        localStorage.removeItem('business_summary');
        window.location.href = '/static/index.html';
    }
}

async function callAgent(agentType) {
    const message = `I need help with ${agentType} planning for my startup.`;
    
    try {
        const response = await fetch('/api/chat', {
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
        alert(`${agentType.charAt(0).toUpperCase() + agentType.slice(1)} Agent Response:\n\n${data.response}`);
        
    } catch (error) {
        alert(`Error calling ${agentType} agent: ${error.message}`);
    }
}
