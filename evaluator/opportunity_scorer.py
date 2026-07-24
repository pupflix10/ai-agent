"""
AI Opportunity Evaluator & Scoring Engine
Evaluates market signals across 4 core dimensions:
1. Demand Volume Score
2. Supply / Competitor Weakness Gap Score
3. AI Solution Fit Score
4. 2-Year $10M+ ARR Scalability Potential Score

Computes weighted composite score (0-10). Triggers Immediate Alert if Score >= 8.5.
"""

import json
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class OpportunityScorer:
    def __init__(self):
        self.immediate_alert_threshold = 8.5

    def evaluate_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a market signal and compute quantitative scalability and viability scores."""
        title = signal.get("title", "")
        desc = signal.get("description", "")
        combined = f"{title} {desc}".lower()

        # 1. Demand Volume Score (0-10)
        demand_score = 7.0
        if any(w in combined for w in ["high demand", "exploding", "missing 40%", "costing $", "paying $"]):
            demand_score = 9.2
        elif any(w in combined for w in ["struggling", "manual", "friction"]):
            demand_score = 8.4

        # 2. Supply Gap Score (0-10)
        supply_gap_score = 6.5
        if any(w in combined for w in ["undersupplied", "lack automated", "terrible", "no tool", "expensive"]):
            supply_gap_score = 9.0
        elif any(w in combined for w in ["manual work", "outsourced"]):
            supply_gap_score = 8.6

        # 3. AI Solution Fit Score (0-10)
        ai_fit_score = 8.0
        if any(w in combined for w in ["compliance", "invoice matching", "voice ai", "automation", "agent"]):
            ai_fit_score = 9.5
        elif any(w in combined for w in ["software", "data", "bot"]):
            ai_fit_score = 8.8

        # 4. 2-Year $10M+ ARR Scalability Score (0-10)
        # Based on ACV (Annual Contract Value) and target market size (B2B Mid-Market / Enterprise vs SMB volume)
        scalability_score = 7.5
        if any(w in combined for w in ["$50k+/year", "$200k+/year", "enterprise", "compliance", "logistics"]):
            scalability_score = 9.4
        elif any(w in combined for w in ["$500-$2,000/month", "smb field services", "high willingness to pay"]):
            scalability_score = 8.8

        # Composite Weighted Score Calculation
        composite_score = round(
            (demand_score * 0.25) +
            (supply_gap_score * 0.25) +
            (ai_fit_score * 0.25) +
            (scalability_score * 0.25), 2
        )

        is_immediate = composite_score >= self.immediate_alert_threshold

        # Estimated Financial Projection
        if scalability_score >= 9.0:
            arr_estimate = "$10M - $25M ARR in 24 months (High ACV B2B)"
            build_effort = "Low-Medium (AI Agent Orchestration + API Integrations)"
        else:
            arr_estimate = "$3M - $8M ARR in 24 months"
            build_effort = "Low (AI Wrapper + Automation Pipeline)"

        return {
            "title": title,
            "source": signal.get("source", "Web Sweep"),
            "url": signal.get("url", ""),
            "description": desc,
            "scores": {
                "demand_volume": demand_score,
                "supply_gap": supply_gap_score,
                "ai_fit": ai_fit_score,
                "scalability_10m": scalability_score,
                "composite": composite_score
            },
            "financial_projection": arr_estimate,
            "build_effort": build_effort,
            "is_immediate_alert": is_immediate,
            "suggested_mvp_concept": self._generate_mvp_concept(title, combined)
        }

    def _generate_mvp_concept(self, title: str, text: str) -> str:
        """Generate actionable MVP concept description."""
        if "compliance" in text:
            return "Build an Agentic Compliance Auditor that connects to GitHub, AWS/GCP, and PostgreSQL to continuously generate EU AI Act & SOC2 audit reports automatically."
        elif "invoice" in text or "supply chain" in text:
            return "Build an AI Operations Agent that ingests PDF invoices, bills of lading, and purchase orders, flags discrepancies, and drafts dispute resolution emails automatically."
        elif "voice" in text or "support" in text:
            return "Deploy a multi-lingual Retell/Vapi Voice AI agent tailored for local home services with instant Google Calendar & Jobber booking integration."
        return "Build a multi-agent workflow solution targeting this specific pain point with a self-service B2B subscription tier."

    def evaluate_batch(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate a list of market signals and return sorted scored opportunities."""
        evaluated = [self.evaluate_signal(s) for s in signals]
        # Sort by composite score descending
        evaluated.sort(key=lambda x: x["scores"]["composite"], reverse=True)
        return evaluated

if __name__ == "__main__":
    scorer = OpportunityScorer()
    sample = {
        "title": "Automated Cross-Platform Regulatory Compliance Monitoring for AI Native Startups",
        "description": "High demand among EU & US fintech startups struggling with manual EU AI Act audit preparation. Enterprise tools cost $50k+/year.",
        "source": "G2 Software Reviews"
    }
    print(json.dumps(scorer.evaluate_signal(sample), indent=2))
