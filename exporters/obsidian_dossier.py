"""
Obsidian Opportunity Dossier Exporter
Exports detailed market research, competitive gap analysis, financial projections,
and AI MVP execution plans directly to Obsidian Second Brain under `02 My Businesses/Opportunities/`
or local `./dossiers/` directory when running in cloud environments (e.g. GitHub Actions).
"""

import os
import re
import logging
from datetime import datetime
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ObsidianDossierExporter:
    def __init__(self, target_dir: str = None):
        default_obsidian = "/Users/a1/Documents/Second Brain/Second Brain/02 My Businesses/Opportunities"
        
        # Check if local Obsidian folder exists or can be created; otherwise fallback to ./dossiers
        if target_dir:
            self.target_dir = target_dir
        else:
            try:
                os.makedirs(default_obsidian, exist_ok=True)
                self.target_dir = default_obsidian
            except (PermissionError, OSError):
                fallback = os.path.join(os.path.dirname(__file__), "..", "dossiers")
                os.makedirs(fallback, exist_ok=True)
                self.target_dir = fallback

        os.makedirs(self.target_dir, exist_ok=True)

    def _sanitize_filename(self, text: str) -> str:
        """Sanitize title for clean filesystem file naming."""
        clean = re.sub(r'[^\w\s-]', '', text).strip()
        clean = re.sub(r'[-\s]+', '-', clean)
        return clean[:60]

    def export_dossier(self, opp: Dict[str, Any]) -> str:
        """Generate and save Obsidian Second Brain research dossier."""
        title = opp.get("title", "Market Opportunity")
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_title = self._sanitize_filename(title)
        filename = f"{date_str} - {safe_title}.md"
        filepath = os.path.join(self.target_dir, filename)

        scores = opp.get("scores", {})
        composite = scores.get("composite", 0.0)

        content = f"""---
tags:
  - project/ai-agent
  - business/02
  - opportunity-hunt
  - high-demand
date: {date_str}
score: {composite}
arr_potential: "{opp.get('financial_projection', '$10M+ ARR')}"
status: open-dossier
---

# 🚀 Opportunity Dossier: {title}

> [!summary] Executive Thesis
> **Score**: `{composite}/10` | **2-Year ARR Potential**: `{opp.get('financial_projection')}`
> This is a high-demand, undersupplied business opportunity identified by the AI Opportunity Hunter. Existing market offerings are either overly expensive, manual, or missing modern agentic AI integration.

---

## 📊 Quantitative Viability Scores

| Evaluation Dimension | Score (0-10) | Evaluation Metrics |
| :--- | :---: | :--- |
| **Demand Volume** | `{scores.get('demand_volume', 'N/A')}` | Verified user pain points across forums, search spikes & reviews |
| **Supply / Competitor Gap** | `{scores.get('supply_gap', 'N/A')}` | Current tools are expensive, slow, or lack automation |
| **AI Solution Fit** | `{scores.get('ai_fit', 'N/A')}` | Problem can be 80%+ solved by AI Agents + Light Human QA |
| **$10M+ 2-Yr Scalability** | `{scores.get('scalability_10m', 'N/A')}` | High B2B ACV potential ($10k-$50k/yr per customer) |
| **COMPOSITE SCORE** | **`{composite}/10`** | **{"🔥 IMMEDIATE ALERT TRIGGERED" if opp.get("is_immediate_alert") else "✅ HIGH VALUE OPPORTUNITY"}** |

---

## 🔍 Problem & Market Demand Analysis

### Source Signal
- **Channel**: `{opp.get('source')}`
- **Reference URL**: [{opp.get('url')}]({opp.get('url')})

### Customer Pain Points
{opp.get('description')}

---

## 🛠️ Recommended AI Product Execution Plan

> [!key-takeaways] Suggested MVP Concept
> {opp.get('suggested_mvp_concept')}

### Recommended Tech Stack & Architecture
- **Agent Orchestration**: Python + Antigravity SDK / LangGraph / CrewAI.
- **Frontend / Client Dashboard**: Next.js + TailwindCSS + Vercel.
- **Data & Integrations**: PostgreSQL + Redis + Vector DB (Pinecone/Qdrant).
- **AI Models**: Gemini 1.5 Pro / Flash for multimodal reasoning + function calling.

### Go-to-Market (GTM) Strategy to $10M ARR
1. **Phase 1 (Months 1-3)**: Direct cold outreach & LinkedIn DMs to 50 target ICPs (Ideal Customer Profiles) for beta pilot ($1k/mo per pilot).
2. **Phase 2 (Months 4-12)**: Product-led content marketing targeting negative reviews of incumbent tools; scale to $1M ARR (100 customers @ $10k ACV).
3. **Phase 3 (Months 13-24)**: Enterprise sales team + API integrations; scale to $10M+ ARR (1,000 customers @ $10k ACV).

---

## 📌 Related Notes & Backlinks
- [[00 - Project MOC]]
- [[2026-07-23 - Project Chat Summary Setup]]
"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Dossier saved successfully to {filepath}")
        return filepath

if __name__ == "__main__":
    exporter = ObsidianDossierExporter()
    sample = {
        "title": "Automated Cross-Platform Regulatory Compliance Monitoring for AI Native Startups",
        "source": "G2 Software Reviews",
        "url": "https://g2.com",
        "description": "High demand among EU & US fintech startups struggling with manual EU AI Act & HIPAA audit preparation.",
        "financial_projection": "$10M - $25M ARR in 24 months",
        "build_effort": "Low-Medium",
        "is_immediate_alert": True,
        "scores": {
            "demand_volume": 9.2,
            "supply_gap": 9.0,
            "ai_fit": 9.5,
            "scalability_10m": 9.4,
            "composite": 9.27
        },
        "suggested_mvp_concept": "Build an Agentic Compliance Auditor that connects to GitHub, AWS/GCP, and PostgreSQL to continuously generate EU AI Act audit reports automatically."
    }
    path = exporter.export_dossier(sample)
    print(f"Exported to: {path}")
