# 🎯 Master System Prompt: AI Business Opportunity Hunter Agent

> **Instructions for Claude**: Copy and paste the prompt below into Claude to generate an upgraded, highly optimized version of the AI Business Opportunity Hunter Agent system.

---

```text
Act as a Principal AI Systems Architect and Lead Python Developer. Build an autonomous, production-grade AI Business Opportunity Hunter Agent system designed to scan global web signals, detect high-demand undersupplied market gaps, evaluate 2-year $10M+ ARR potential, dispatch email alerts, export Obsidian Second Brain dossiers, and run 24/7 in the cloud via GitHub Actions.

Here is the exact technical specification for the complete codebase:

---

### 1. System Vision & Architecture Overview
Build a modular Python application with the following components:
1. **Multi-Source Market Hunter (`scrapers/multi_source_hunter.py`)**
   - Sweeps Reddit subreddits (r/SaaS, r/startups, r/ProblemFinder, r/smallbusiness, r/automation) scanning for explicit user pain points ("I wish there was...", "Paying $X for terrible software", "Manual work gap").
   - Synthesizes 1-star/2-star G2 & Capterra software reviews to spot missing features in incumbent tools.
   - Parses search volume spikes (Google Trends API / Exploding Topics).
   - Scans high-budget B2B job requests (Upwork / Freelance platforms).

2. **$10M+ ARR Opportunity Scorer (`evaluator/opportunity_scorer.py`)**
   - Evaluates each candidate signal across 4 quantitative dimensions (0–10 scale):
     a) Demand Volume Score (0-10)
     b) Supply & Competitor Weakness Gap Score (0-10)
     c) AI Solution Fit Score (0-10)
     d) 2-Year $10M+ ARR Scalability Potential Score (0-10)
   - Computes weighted composite score: Composite = (Demand*0.25) + (Supply*0.25) + (AI_Fit*0.25) + (Scalability*0.25).
   - Triggers `is_immediate_alert = True` whenever Composite Score >= 8.5/10.
   - Generates actionable MVP Architecture, recommended tech stack, and 3-phase Go-to-Market (GTM) execution strategy ($0 -> $1M -> $10M ARR).

3. **Email Notification Engine (`notifications/email_notifier.py`)**
   - Built with native Python `smtplib` (Zero 3rd-party paid APIs required).
   - Uses Gmail SMTP + App Password authentication with environment variables (`NOTIFY_EMAIL_FROM`, `NOTIFY_EMAIL_PASSWORD`, `NOTIFY_EMAIL_TO`).
   - Dispatches beautifully styled HTML emails:
     - **Immediate Alert**: Instant alert when composite score >= 8.5.
     - **Bi-Daily Digest**: 48-hour digest summarizing top market gaps.

4. **Obsidian Second Brain Exporter (`exporters/obsidian_dossier.py`)**
   - Generates detailed Markdown dossiers formatted for Obsidian.
   - Includes YAML frontmatter (`tags: [project/ai-agent, business/02, opportunity-hunt]`, `score`, `arr_potential`, `date`).
   - Includes Obsidian callouts (`> [!summary]`, `> [!info]`, `> [!key-takeaways]`, `> [!todo]`), scoring tables, and `[[WikiLinks]]`.
   - Cloud-resilient: Writes to `/Users/a1/Documents/Second Brain/Second Brain/02 My Businesses/Opportunities/` when running on Mac, and gracefully falls back to `./dossiers/` when running in cloud CI/CD.

5. **Agent Daemon & CLI Runner (`scheduler/agent_daemon.py` & `main.py`)**
   - Manages process deduplication, 48-hour digest schedules, and hunt execution cycles.
   - Provides CLI commands:
     - `python main.py --scan` (Run full hunt cycle)
     - `python main.py --status` (Check live agent fleet status)
     - `python main.py --start` / `python main.py --stop` (Control background jobs)
     - `python main.py --test-email` (Send test email alert)

6. **24/7 Cloud Autopilot (`.github/workflows/opportunity_hunter.yml`)**
   - GitHub Actions workflow running on schedule `cron: '0 0,12 * * *'` (twice a day).
   - 100% free cloud execution requiring zero Mac battery or computer uptime.
   - Configured with `permissions: contents: write` to safely commit new dossiers back to the repository.

7. **Multi-Agent Command Center Dashboard (`dashboard/index.html`, `style.css`, `app.js`)**
   - Single Page App dashboard with dark mode glassmorphism UI.
   - Displays active agent fleet grid, live email alert outbox, top $10M+ opportunities, and Obsidian vault sync.
   - Includes "+ Add New Agent" modal for future-proofing.

---

### Output Requirements
Generate clean, complete, production-ready code files for the entire project folder structure with no placeholders or missing imports. Provide step-by-step instructions for installation and deployment.
```
