const summary = localStorage.getItem('business_summary');
if (summary) {
    const summaryData = JSON.parse(summary);
    const reportElement = document.getElementById('fullReport');
    if (reportElement) {
        reportElement.innerHTML = `
            <div style="margin-top: 2rem; padding: 1.5rem; background: rgba(88, 166, 255, 0.1); border-radius: 8px;">
                <h3 style="margin-bottom: 1rem;">Complete Business Plan</h3>
                <pre style="white-space: pre-wrap; color: #c9d1d9;">${JSON.stringify(summaryData, null, 2)}</pre>
            </div>
        `;
    }
}

function exportPlan() {
    const summary = localStorage.getItem('business_summary');
    if (!summary) {
        alert('No business plan found. Please complete the survey first.');
        return;
    }
    
    const blob = new Blob([summary], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'hardlaunch-business-plan.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function editPlan() {
    window.location.href = '/static/dashboard.html';
}

function nextStage() {
    alert('Next stage functionality coming soon!');
}
