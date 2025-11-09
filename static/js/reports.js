window.sessionId = window.sessionId || localStorage.getItem('hardlaunch_session_id');

async function generateComprehensivePlan() {
    const summary = localStorage.getItem('business_summary');
    if (!summary) {
        alert('Please complete the business survey first before generating a plan.');
        window.location.href = '/static/index.html';
        return;
    }

    const generateBtn = document.getElementById('generatePlanBtn');
    const exportBtn = document.getElementById('exportPdfBtn');
    const planStatus = document.getElementById('planStatus');
    const planContent = document.getElementById('planContent');
    
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="button-icon">⏳</span> Generating Plan...';
    
    planStatus.innerHTML = `
        <div class="status-message loading">
            <div class="spinner"></div>
            <p>Consulting with all specialized agents to create your comprehensive plan...</p>
            <p class="status-detail">This may take 30-60 seconds. Please wait.</p>
        </div>
    `;
    planStatus.style.display = 'block';

    try {
        const summaryData = JSON.parse(summary);
        const businessIdea = summaryData.idea || summaryData.summary || 'your startup';
        
        const sections = [
            {
                id: 'executiveSummary',
                query: `Create an executive summary for ${businessIdea}. Include the problem, solution, target market, and unique value proposition in 3-4 paragraphs.`,
                agentType: 'business'
            },
            {
                id: 'businessStrategy',
                query: `Provide a detailed business strategy for ${businessIdea}. Include business model, revenue streams, customer segments, and growth roadmap.`,
                agentType: 'business'
            },
            {
                id: 'financialPlan',
                query: `Create a financial plan for ${businessIdea}. Include budget estimates, pricing strategy, funding recommendations, and key financial milestones.`,
                agentType: 'finance'
            },
            {
                id: 'marketAnalysis',
                query: `Provide market analysis for ${businessIdea}. Include TAM/SAM/SOM, competitive landscape, go-to-market strategy, and customer acquisition channels.`,
                agentType: 'market'
            },
            {
                id: 'technicalArchitecture',
                query: `Recommend technical architecture for ${businessIdea}. Include tech stack, system architecture, integrations, and development roadmap.`,
                agentType: 'engineering'
            }
        ];

        for (let i = 0; i < sections.length; i++) {
            const section = sections[i];
            planStatus.innerHTML = `
                <div class="status-message loading">
                    <div class="spinner"></div>
                    <p>Generating ${section.id.replace(/([A-Z])/g, ' $1').trim()}... (${i + 1}/${sections.length})</p>
                </div>
            `;

            const response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: window.sessionId,
                    message: section.query,
                    agent_type: section.agentType
                })
            });

            const data = await response.json();
            const sectionElement = document.getElementById(section.id);
            const contentElement = sectionElement.querySelector('.section-content');
            contentElement.innerHTML = parseMarkdown(data.response);
        }

        const nextStepsQuery = `Based on all our discussions about ${businessIdea}, provide specific next steps and action items prioritized by importance.`;
        const nextStepsResponse = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: window.sessionId,
                message: nextStepsQuery,
                agent_type: 'business'
            })
        });
        const nextStepsData = await nextStepsResponse.json();
        document.getElementById('nextSteps').querySelector('.section-content').innerHTML = parseMarkdown(nextStepsData.response);

        document.getElementById('planTitle').textContent = `Startup Plan: ${summaryData.idea || 'Your Business'}`;
        document.getElementById('planDate').textContent = `Generated on ${new Date().toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        })}`;

        planStatus.innerHTML = `
            <div class="status-message success">
                <span class="status-icon">✅</span>
                <p>Comprehensive plan generated successfully!</p>
            </div>
        `;
        
        setTimeout(() => {
            planStatus.style.display = 'none';
        }, 3000);

        planContent.style.display = 'block';
        exportBtn.style.display = 'inline-flex';
        generateBtn.innerHTML = '<span class="button-icon">🔄</span> Regenerate Plan';
        generateBtn.disabled = false;

    } catch (error) {
        planStatus.innerHTML = `
            <div class="status-message error">
                <span class="status-icon">❌</span>
                <p>Error generating plan: ${error.message}</p>
                <p class="status-detail">Please try again.</p>
            </div>
        `;
        generateBtn.innerHTML = '<span class="button-icon">✨</span> Generate Comprehensive Plan';
        generateBtn.disabled = false;
    }
}

async function exportToPDF() {
    const element = document.getElementById('planDocument');
    const exportBtn = document.getElementById('exportPdfBtn');
    
    exportBtn.disabled = true;
    exportBtn.innerHTML = '<span class="button-icon">⏳</span> Exporting...';

    const opt = {
        margin: 0.5,
        filename: 'startup-plan.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    };

    try {
        await html2pdf().set(opt).from(element).save();
        exportBtn.innerHTML = '<span class="button-icon">✅</span> Exported!';
        setTimeout(() => {
            exportBtn.innerHTML = '<span class="button-icon">📄</span> Export as PDF';
            exportBtn.disabled = false;
        }, 2000);
    } catch (error) {
        alert('Error exporting PDF: ' + error.message);
        exportBtn.innerHTML = '<span class="button-icon">📄</span> Export as PDF';
        exportBtn.disabled = false;
    }
}

document.getElementById('generatePlanBtn').addEventListener('click', generateComprehensivePlan);
document.getElementById('exportPdfBtn').addEventListener('click', exportToPDF);
