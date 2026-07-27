"""
AI Opportunity Evaluator & Scoring Engine
Evaluates market signals across 4 core dimensions:
1. Demand Volume Score
2. Supply / Competitor Weakness Gap Score
3. AI Solution Fit Score
4. 2-Year $10M+ ARR Scalability Potential Score

Strict Filters: Requires explicit B2B business intent and monetary budget.
Triggers Immediate Alert ONLY if Composite Score >= 9.5/10.
"""

import json
import logging
import re
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class OpportunityScorer:
    def __init__(self):
        # Strict threshold: Only true unicorn B2B opportunities trigger immediate alert
        self.immediate_alert_threshold = 9.5

    def is_irrelevant_tech_news(self, text: str) -> bool:
        """Filter out general tech news, gaming, hardware, or consumer opinion posts."""
        t = text.lower()
        irrelevant_topics = [
            r"nvidia", r"cpu", r"gopro", r"roku", r"apple", r"sound card", r"bmw",
            r"infotainment", r"atari", r"gaming", r"beavis", r"kids act", r"police officer",
            r"outlook", r"grapheneos", r"django", r"decoupling capacitor", r"steam machine"
        ]
        return any(re.search(pat, t) for pat in irrelevant_topics)

    def evaluate_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a market signal and compute quantitative scalability and viability scores."""
        title = signal.get("title", "")
        desc = signal.get("description", "")
        combined = f"{title} {desc}".lower()

        # Discard irrelevant tech news or consumer chatter
        if self.is_irrelevant_tech_news(combined):
            return self._build_low_score_result(signal, "Irrelevant Tech News / Consumer Chatter")

        # Must have explicit B2B business intent or spending budget
        b2b_budget_keywords = [
            "company", "business", "clients", "customers", "spending $", "paying $",
            "costing $", "our team", "manual work", "workflow", "compliance",
            "invoice", "audit", "b2b", "saas", "agency"
        ]
        has_b2b_context = any(kw in combined for kw in b2b_budget_keywords)

        if not has_b2b_context:
            return self._build_low_score_result(signal, "Lacks B2B Business Budget/Context")

        # 1. Demand Volume Score (0-10)
        demand_score = 6.0
        if any(w in combined for w in ["paying $", "costing $", "spending $", "high demand", "desperately need"]):
            demand_score = 9.5
        elif any(w in combined for w in ["manual work", "frustrating", "struggling with"]):
            demand_score = 8.2

        # 2. Supply Gap Score (0-10)
        supply_gap_score = 5.5
        if any(w in combined for w in ["no good software", "terrible tools", "lack automation", "expensive enterprise"]):
            supply_gap_score = 9.2
        elif any(w in combined for w in ["doing it manually", "outsourced"]):
            supply_gap_score = 8.0

        # 3. AI Solution Fit Score (0-10)
        ai_fit_score = 6.0
        if any(w in combined for w in ["compliance", "invoice", "audit", "automation", "document processing", "voice agent"]):
            ai_fit_score = 9.5
        elif any(w in combined for w in ["data", "software", "workflow"]):
            ai_fit_score = 8.0

        # 4. 2-Year $10M+ ARR Scalability Score (0-10)
        scalability_score = 5.5
        if any(w in combined for w in ["enterprise", "$10k", "$50k", "b2b", "compliance", "fintech"]):
            scalability_score = 9.2
        elif any(w in combined for w in ["smb", "agency", "subscription"]):
            scalability_score = 7.5

        composite_score = round(
            (demand_score * 0.25) +
            (supply_gap_score * 0.25) +
            (ai_fit_score * 0.25) +
            (scalability_score * 0.25), 2
        )

        is_immediate = composite_score >= self.immediate_alert_threshold

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
            "financial_projection": "$10M+ ARR Potential" if composite_score >= 8.5 else "$1M-$5M ARR",
            "build_effort": "Low-Medium (AI Agent System)",
            "is_immediate_alert": is_immediate,
            "suggested_mvp_concept": f"Build a targeted AI workflow solution for {title[:40]}."
        }

    def _build_low_score_result(self, signal: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """Return a filtered out low score result."""
        return {
            "title": signal.get("title", ""),
            "source": signal.get("source", ""),
            "url": signal.get("url", ""),
            "description": signal.get("description", ""),
            "scores": {
                "demand_volume": 2.0,
                "supply_gap": 2.0,
                "ai_fit": 2.0,
                "scalability_10m": 2.0,
                "composite": 2.0
            },
            "financial_projection": "Low Scalability",
            "build_effort": "N/A",
            "is_immediate_alert": False,
            "suggested_mvp_concept": f"Filtered: {reason}"
        }

    def evaluate_batch(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate signals and return scored B2B opportunities."""
        evaluated = [self.evaluate_signal(s) for s in signals]
        # Filter out anything with composite score < 7.0
        high_quality = [e for e in evaluated if e["scores"]["composite"] >= 7.0]
        high_quality.sort(key=lambda x: x["scores"]["composite"], reverse=True)
        return high_quality

if __name__ == "__main__":
    scorer = OpportunityScorer()
    sample = {
        "title": "Nvidia CPU system for Windows PCs",
        "description": "Tech news post about Nvidia hardware",
        "source": "Hacker News"
    }
    print(json.dumps(scorer.evaluate_signal(sample), indent=2))
