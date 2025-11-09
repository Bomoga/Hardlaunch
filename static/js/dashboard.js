window.sessionId = window.sessionId || localStorage.getItem('hardlaunch_session_id');

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

const summary = localStorage.getItem('business_summary');
if (summary) {
    const summaryData = JSON.parse(summary);
    const summaryElement = document.getElementById('businessSummary');
    if (summaryElement) {
        let html = '<div style="line-height: 1.8;">';
        
        if (summaryData.idea) {
            html += `
                <div style="margin-bottom: 1.5rem;">
                    <strong style="color: #58a6ff; font-size: 1.1rem;">💡 Your Idea</strong>
                    <p style="margin-top: 0.5rem; padding-left: 1rem; border-left: 3px solid #58a6ff;">
                        ${summaryData.idea}
                    </p>
                </div>
            `;
        }
        
        if (summaryData.target_audience) {
            html += `
                <div style="margin-bottom: 1.5rem;">
                    <strong style="color: #58a6ff; font-size: 1.1rem;">🎯 Target Audience</strong>
                    <p style="margin-top: 0.5rem; padding-left: 1rem; border-left: 3px solid #58a6ff;">
                        ${summaryData.target_audience}
                    </p>
                </div>
            `;
        }
        
        if (summaryData.competitive_advantage) {
            html += `
                <div style="margin-bottom: 1.5rem;">
                    <strong style="color: #58a6ff; font-size: 1.1rem;">🏆 Competitive Advantage</strong>
                    <p style="margin-top: 0.5rem; padding-left: 1rem; border-left: 3px solid #58a6ff;">
                        ${summaryData.competitive_advantage}
                    </p>
                </div>
            `;
        }
        
        if (summaryData.constraints) {
            html += `
                <div style="margin-bottom: 1.5rem;">
                    <strong style="color: #58a6ff; font-size: 1.1rem;">⚠️ Constraints</strong>
                    <p style="margin-top: 0.5rem; padding-left: 1rem; border-left: 3px solid #58a6ff;">
                        ${summaryData.constraints}
                    </p>
                </div>
            `;
        }
        
        if (summaryData.summary) {
            html += `
                <div style="margin-bottom: 1.5rem;">
                    <strong style="color: #58a6ff; font-size: 1.1rem;">📋 AI Summary</strong>
                    <p style="margin-top: 0.5rem; padding-left: 1rem; border-left: 3px solid #58a6ff;">
                        ${summaryData.summary}
                    </p>
                </div>
            `;
        }
        
        html += '</div>';
        summaryElement.innerHTML = html;
    }
} else {
    const summaryElement = document.getElementById('businessSummary');
    if (summaryElement) {
        summaryElement.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #6e7681;">
                <p style="margin-bottom: 1rem;">No business summary available yet.</p>
                <p style="margin-bottom: 1.5rem;">Complete the survey to get started!</p>
                <a href="/static/survey.html" style="padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #4c8dd6, #2d5fa3); color: white; text-decoration: none; border-radius: 8px; display: inline-block;">
                    Start Survey
                </a>
            </div>
        `;
    }
}

function revertToSurvey() {
    if (confirm('Are you sure you want to restart the survey? This will clear your current session.')) {
        localStorage.removeItem('hardlaunch_session_id');
        localStorage.removeItem('business_summary');
        window.location.href = '/static/survey.html';
    }
}

async function callAgent(agentType) {
    const summary = localStorage.getItem('business_summary');
    if (!summary) {
        alert('Please complete the initial business survey before using specialized agents.');
        window.location.href = '/static/survey.html';
        return;
    }
    
    const status = await fetch(`/api/submission-status?session_id=${window.sessionId}`).then(r => r.json());
    
    if (!status.submitted) {
        alert('Please submit your business summary first. Go to the Survey page and tell the agent you\'re ready to submit.');
        window.location.href = '/static/survey.html';
        return;
    }
    
    const agentPages = {
        'business': '/static/agent-business.html',
        'finance': '/static/agent-finance.html',
        'market': '/static/agent-market.html',
        'engineering': '/static/agent-engineering.html'
    };
    
    const page = agentPages[agentType];
    if (page) {
        window.location.href = page;
    }
}

async function checkDashboardAccess() {
    const sessionId = window.sessionId || localStorage.getItem('hardlaunch_session_id');
    if (!sessionId) return;
    
    try {
        const status = await fetch(`/api/submission-status?session_id=${sessionId}`).then(r => r.json());
        
        if (!status.submitted && status.hasSummary) {
            const warningDiv = document.createElement('div');
            warningDiv.style.cssText = 'background: rgba(255, 193, 7, 0.1); border: 2px solid #ffc107; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; text-align: center;';
            warningDiv.innerHTML = `
                <h3 style="color: #ffc107; margin-bottom: 0.5rem;">⚠️ Survey Not Submitted</h3>
                <p style="color: #c9d1d9;">Your business summary is saved but not yet submitted. To access specialized agents, return to the Survey page and tell the agent you're ready to submit.</p>
                <a href="/static/survey.html" style="display: inline-block; margin-top: 1rem; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #ffc107, #ff9800); color: #0a1628; text-decoration: none; border-radius: 8px; font-weight: 600;">
                    Go to Survey Page →
                </a>
            `;
            
            const container = document.querySelector('.dashboard-page');
            if (container) {
                container.insertBefore(warningDiv, container.firstChild);
            }
            
            const agentButtons = document.querySelectorAll('.agent-button');
            agentButtons.forEach(btn => {
                if (!btn.onclick.toString().includes('revertToSurvey')) {
                    btn.style.opacity = '0.5';
                    btn.style.cursor = 'not-allowed';
                }
            });
        }
    } catch (error) {
        console.error('Error checking dashboard access:', error);
    }
}

document.addEventListener('DOMContentLoaded', checkDashboardAccess);
