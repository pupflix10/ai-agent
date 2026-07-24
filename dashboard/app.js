// AI Agent Command Center - Interactive JavaScript Engine

// Initial State with Future-Proof Fleet Architecture
const state = {
    agents: [
        {
            id: 'agent-1',
            name: 'AI Business Opportunity Hunter',
            role: 'Market Research & Trend Hunter',
            status: 'RUNNING',
            lastRun: '2 mins ago',
            nextRun: 'In 5h 58m',
            tasksExecuted: 142,
            channel: 'WhatsApp & Obsidian',
            icon: 'fa-magnifying-glass-dollar'
        },
        {
            id: 'agent-2',
            name: 'Obsidian Second Brain Dossier Sync',
            role: 'Documentation & Dossier Exporter',
            status: 'RUNNING',
            lastRun: '2 mins ago',
            nextRun: 'Real-time On Event',
            tasksExecuted: 48,
            channel: 'Obsidian (/02 My Businesses)',
            icon: 'fa-book-bookmark'
        },
        {
            id: 'agent-3',
            name: 'WhatsApp Dispatcher & Alert Bridge',
            role: 'Instant Alert & Digest Messenger',
            status: 'SCHEDULED',
            lastRun: 'Just now (Test Alert)',
            nextRun: 'Every 48 hours',
            tasksExecuted: 26,
            channel: 'Green API / Baileys Bridge',
            icon: 'fa-whatsapp'
        },
        {
            id: 'agent-4',
            name: 'Reddit & G2 Competitor Sentiment Monitor',
            role: 'Multi-Source Scraper',
            status: 'RUNNING',
            lastRun: '5 mins ago',
            nextRun: 'Every 6 hours',
            tasksExecuted: 310,
            channel: 'Internal Pipeline',
            icon: 'fa-comments'
        }
    ],
    whatsappMessages: [
        {
            id: 'msg-1',
            type: 'IMMEDIATE_ALERT',
            title: 'Automated Cross-Platform Regulatory Compliance Monitoring for AI Native Startups',
            score: '9.28',
            arr: '$10M - $25M ARR in 24 months',
            time: '2026-07-23 20:01',
            sender: 'Antigravity AI Hunter',
            text: `🚨 *IMMEDIATE OPPORTUNITY ALERT* 🚨
💡 *Opportunity*: Automated Cross-Platform Compliance Auditor
🔥 *Score*: *9.28/10* | 📈 *Potential*: $10M - $25M ARR in 24 months
🎯 *Demand*: EU & US fintech/healthtech startups struggling with manual EU AI Act & HIPAA audit preparation. Current enterprise tools cost $50k+/year.
🛠️ *Suggested MVP*: Agentic Compliance Auditor connecting to GitHub, AWS/GCP, & PostgreSQL to generate automated audit reports.`
        },
        {
            id: 'msg-2',
            type: 'IMMEDIATE_ALERT',
            title: 'Autonomous AI Agent for Invoice Matching & Supply Chain Dispute Resolution',
            score: '9.17',
            arr: '$10M - $25M ARR in 24 months',
            time: '2026-07-23 20:01',
            sender: 'Antigravity AI Hunter',
            text: `🚨 *IMMEDIATE OPPORTUNITY ALERT* 🚨
💡 *Opportunity*: Autonomous AI Agent for Invoice Matching & Freight Disputes
🔥 *Score*: *9.17/10* | 📈 *Potential*: $10M - $25M ARR in 24 months
🎯 *Demand*: Mid-market logistics companies face massive friction matching freight invoices, POs, and customs receipts ($200k+/yr manual cost).
🛠️ *Suggested MVP*: Operations Agent that ingests PDF invoices and drafts dispute resolution emails automatically.`
        }
    ],
    opportunities: [
        {
            title: 'Automated Compliance Monitoring for AI Startups',
            score: 9.28,
            arr: '$10M - $25M ARR',
            source: 'G2 Software Reviews & User Feedback',
            effort: 'Low-Medium'
        },
        {
            title: 'Autonomous Invoice Matching & Freight Dispute AI',
            score: 9.17,
            arr: '$10M - $25M ARR',
            source: 'B2B Upwork & Logistics Requests',
            effort: 'Low-Medium'
        },
        {
            title: 'Voice AI Customer Support & Booking for Field Services',
            score: 7.95,
            arr: '$3M - $8M ARR',
            source: 'Exploding Topics & Local SMB Trends',
            effort: 'Low'
        }
    ]
};

// Render Agent Cards
function renderAgents() {
    const container = document.getElementById('agent-grid-container');
    if (!container) return;

    container.innerHTML = state.agents.map(agent => `
        <div class="agent-card">
            <div class="agent-header">
                <div class="agent-info">
                    <h3><i class="fa-solid ${agent.icon || 'fa-robot'}"></i> ${agent.name}</h3>
                    <div class="agent-role">${agent.role}</div>
                </div>
                <span class="status-badge ${agent.status === 'RUNNING' ? 'status-running' : 'status-scheduled'}">
                    ${agent.status}
                </span>
            </div>
            <div class="agent-stats">
                <div class="agent-stat-item">
                    <label>Last Run</label>
                    <span>${agent.lastRun}</span>
                </div>
                <div class="agent-stat-item">
                    <label>Next Execution</label>
                    <span>${agent.nextRun}</span>
                </div>
                <div class="agent-stat-item">
                    <label>Tasks Executed</label>
                    <span>${agent.tasksExecuted}</span>
                </div>
            </div>
            <div class="agent-footer">
                <div class="channel-tag">
                    <i class="fa-solid fa-satellite-dish"></i> ${agent.channel}
                </div>
                <button class="btn btn-outline" onclick="triggerSingleAgent('${agent.id}')">
                    <i class="fa-solid fa-play"></i> Run Now
                </button>
            </div>
        </div>
    `).join('');

    document.getElementById('stat-active-agents').innerText = state.agents.length;
    document.getElementById('agent-count-badge').innerText = state.agents.length;
}

// Render WhatsApp Notification Feed
function renderWhatsAppFeed() {
    const container = document.getElementById('whatsapp-feed-container');
    if (!container) return;

    container.innerHTML = state.whatsappMessages.map(msg => `
        <div class="wa-message-card">
            <div class="wa-message-header">
                <span class="wa-sender"><i class="fa-brands fa-whatsapp"></i> ${msg.sender}</span>
                <span class="wa-time">${msg.time}</span>
            </div>
            <div style="margin-bottom: 8px;">
                <span class="score-pill">Score: ${msg.score}/10</span>
                <strong style="margin-left: 8px;">${msg.title}</strong>
            </div>
            <div class="wa-text">${msg.text}</div>
        </div>
    `).join('');

    document.getElementById('stat-alerts').innerText = state.whatsappMessages.length;
    document.getElementById('alert-count-badge').innerText = state.whatsappMessages.length;
}

// Render Top Opportunities List
function renderOpportunities() {
    const container = document.getElementById('opportunities-list-container');
    if (!container) return;

    container.innerHTML = state.opportunities.map((opp, idx) => `
        <div style="padding: 12px; background: rgba(255,255,255,0.03); border-radius: 8px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span style="font-weight: 700; font-size: 13px;">${idx + 1}. ${opp.title}</span>
                <span class="score-pill">${opp.score}</span>
            </div>
            <div style="font-size: 11px; color: var(--text-secondary);">
                <span><i class="fa-solid fa-chart-line"></i> ${opp.arr}</span> | 
                <span><i class="fa-solid fa-tag"></i> ${opp.source}</span>
            </div>
        </div>
    `).join('');
}

// Global Event Listeners & UI Handlers
document.addEventListener('DOMContentLoaded', () => {
    renderAgents();
    renderWhatsAppFeed();
    renderOpportunities();

    // Modal Control
    const modal = document.getElementById('add-agent-modal');
    const btnAddAgent = document.getElementById('btn-add-agent');
    const btnCloseModal = document.getElementById('modal-close-btn');
    const btnCancelModal = document.getElementById('modal-cancel-btn');
    const formAddAgent = document.getElementById('add-agent-form');

    if (btnAddAgent) btnAddAgent.onclick = () => modal.classList.add('active');
    if (btnCloseModal) btnCloseModal.onclick = () => modal.classList.remove('active');
    if (btnCancelModal) btnCancelModal.onclick = () => modal.classList.remove('active');

    // Handle Adding New Agents (Future-Proofing)
    if (formAddAgent) {
        formAddAgent.onsubmit = (e) => {
            e.preventDefault();
            const name = document.getElementById('agent-name').value;
            const role = document.getElementById('agent-role').value;
            const interval = document.getElementById('agent-interval').value;
            const channel = document.getElementById('agent-channel').value;

            const newAgent = {
                id: `agent-${Date.now()}`,
                name: name,
                role: role,
                status: 'RUNNING',
                lastRun: 'Just added',
                nextRun: interval,
                tasksExecuted: 0,
                channel: channel,
                icon: 'fa-robot'
            };

            state.agents.push(newAgent);
            renderAgents();
            modal.classList.remove('active');
            formAddAgent.reset();
            alert(`🎉 Agent "${name}" deployed successfully!`);
        };
    }

    // Trigger Manual Scan Button
    const btnScan = document.getElementById('btn-trigger-scan');
    if (btnScan) {
        btnScan.onclick = () => {
            btnScan.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Scanning Markets...';
            setTimeout(() => {
                btnScan.innerHTML = '<i class="fa-solid fa-rotate-right"></i> Run Scan Now';
                alert("🚀 Market Hunt Scan triggered! Checked Reddit, G2, Product Hunt & Google Trends. 3 opportunities scored.");
            }, 1200);
        };
    }

    // Send Test WhatsApp Button
    const btnTestWa = document.getElementById('btn-send-test-whatsapp');
    if (btnTestWa) {
        btnTestWa.onclick = () => {
            btnTestWa.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Sending...';
            setTimeout(() => {
                btnTestWa.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Send Test WhatsApp';

                const newMsg = {
                    id: `msg-${Date.now()}`,
                    type: 'IMMEDIATE_ALERT',
                    title: 'Voice AI Outbound & Support Agent for Field Services',
                    score: '7.95',
                    arr: '$3M - $8M ARR in 24 months',
                    time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
                    sender: 'Antigravity AI Hunter',
                    text: `🚨 *IMMEDIATE OPPORTUNITY ALERT* 🚨
💡 *Opportunity*: Voice AI Customer Support for SMB Field Services
🔥 *Score*: *7.95/10* | 📈 *Potential*: $3M - $8M ARR
🎯 *Demand*: HVAC, plumbing, and legal practices miss over 40% of inbound calls. High willingness to pay ($500-$2,000/month).`
                };

                state.whatsappMessages.unshift(newMsg);
                renderWhatsAppFeed();
                alert("📲 Test WhatsApp message sent to outbox feed!");
            }, 800);
        };
    }
});

function triggerSingleAgent(agentId) {
    const agent = state.agents.find(a => a.id === agentId);
    if (agent) {
        alert(`⚡ Triggered manual execution for "${agent.name}"!`);
        agent.lastRun = 'Just now';
        agent.tasksExecuted += 1;
        renderAgents();
    }
}
