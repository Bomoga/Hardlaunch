window.sessionId = window.sessionId || localStorage.getItem('hardlaunch_session_id');

const reportPrompts = {
    business: 'Generate a comprehensive Business Planning Report that includes: 1) Executive Summary with problem, solution, and value proposition, 2) Business Model with revenue streams and cost structure, 3) Target Market and Customer Segments, 4) Strategic Roadmap with key milestones, 5) Risk Assessment and mitigation strategies. Format with clear headings and detailed explanations.',
    finance: 'Generate a comprehensive Financial Report that includes: 1) Budget Breakdown with estimated costs for each major category, 2) Pricing Strategy and justification, 3) Revenue Projections for the first 12-24 months, 4) Funding Recommendations with specific funding sources and amounts, 5) Key Financial Milestones and metrics to track. Format with clear headings and specific numbers where possible.',
    market: 'Generate a comprehensive Market Analysis Report that includes: 1) Market Size Analysis with TAM, SAM, and SOM calculations and justifications, 2) Competitive Landscape with direct and indirect competitors, 3) Competitive Advantages and differentiation strategy, 4) Go-to-Market Strategy with specific channels and tactics, 5) Customer Acquisition Plan with estimated CAC and LTV. Format with clear headings and detailed analysis.',
    engineering: 'Generate a comprehensive Engineering Report that includes: 1) Recommended Tech Stack with justifications for each technology choice, 2) System Architecture with key components and their interactions, 3) Third-party Integrations and APIs needed, 4) Development Roadmap with phases and timeline estimates, 5) Technical Risks and infrastructure considerations. Format with clear headings and technical depth.'
};

const reportTitles = {
    business: 'Business Planning Report',
    finance: 'Financial Report',
    market: 'Market Analysis Report',
    engineering: 'Engineering Report'
};

async function checkSurveyCompletion() {
    const summary = localStorage.getItem('business_summary');
    const surveyWarning = document.getElementById('surveyWarning');
    const reportsGrid = document.getElementById('reportsGrid');
    
    if (!summary) {
        surveyWarning.style.display = 'block';
        reportsGrid.style.display = 'none';
        return false;
    }
    
    try {
        const status = await fetch(`/api/submission-status?session_id=${window.sessionId}`).then(r => r.json());
        
        if (!status.submitted) {
            surveyWarning.querySelector('h3').textContent = '⚠️ Survey Not Submitted';
            surveyWarning.querySelector('p').textContent = 'Please submit your business summary first. Go to the Home page and tell the agent you\'re ready to submit.';
            surveyWarning.style.display = 'block';
            reportsGrid.style.display = 'none';
            return false;
        }
    } catch (error) {
        console.error('Error checking submission status:', error);
    }
    
    surveyWarning.style.display = 'none';
    reportsGrid.style.display = 'grid';
    return true;
}

async function generateReport(agentType) {
    const summary = localStorage.getItem('business_summary');
    if (!summary) {
        alert('Please complete the business survey first.');
        window.location.href = '/static/survey.html';
        return;
    }
    
    const status = await fetch(`/api/submission-status?session_id=${window.sessionId}`).then(r => r.json());
    if (!status.submitted) {
        alert('Please submit your business summary first. Go to the Survey page and tell the agent you\'re ready to submit.');
        window.location.href = '/static/survey.html';
        return;
    }

    const card = document.querySelector(`.report-card[data-agent="${agentType}"]`);
    const generateBtn = card.querySelector('.generate-report-btn');
    const exportBtn = card.querySelector('.export-report-btn');
    const contentDiv = card.querySelector('.report-content');
    
    generateBtn.disabled = true;
    generateBtn.textContent = 'Generating...';
    
    try {
        const summaryData = JSON.parse(summary);
        const businessIdea = summaryData.idea || summaryData.summary || 'your startup';
        
        const prompt = `For the business idea: "${businessIdea}"\n\n${reportPrompts[agentType]}`;
        
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: window.sessionId,
                message: prompt,
                agent_type: agentType
            })
        });

        const data = await response.json();
        
        contentDiv.innerHTML = `
            <div class="report-header-doc">
                <h3>${reportTitles[agentType]}</h3>
                <p class="report-date">Generated on ${new Date().toLocaleDateString('en-US', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                })}</p>
            </div>
            <div class="report-body">${parseMarkdown(data.response)}</div>
        `;
        contentDiv.style.display = 'block';
        exportBtn.style.display = 'block';
        generateBtn.textContent = 'Regenerate Report';
        generateBtn.disabled = false;

    } catch (error) {
        alert('Error generating report: ' + error.message);
        generateBtn.textContent = 'Generate Report';
        generateBtn.disabled = false;
    }
}

async function exportReport(agentType) {
    const card = document.querySelector(`.report-card[data-agent="${agentType}"]`);
    const contentDiv = card.querySelector('.report-content');
    const exportBtn = card.querySelector('.export-report-btn');
    
    exportBtn.disabled = true;
    exportBtn.textContent = 'Exporting...';

    const opt = {
        margin: 0.5,
        filename: `${agentType}-report.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    };

    try {
        await html2pdf().set(opt).from(contentDiv).save();
        exportBtn.textContent = 'Exported!';
        setTimeout(() => {
            exportBtn.textContent = 'Export PDF';
            exportBtn.disabled = false;
        }, 2000);
    } catch (error) {
        alert('Error exporting PDF: ' + error.message);
        exportBtn.textContent = 'Export PDF';
        exportBtn.disabled = false;
    }
}

document.querySelectorAll('.generate-report-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const agentType = e.target.dataset.agent;
        generateReport(agentType);
    });
});

document.querySelectorAll('.export-report-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const agentType = e.target.dataset.agent;
        exportReport(agentType);
    });
});

document.addEventListener('DOMContentLoaded', async () => {
    await checkSurveyCompletion();
});
