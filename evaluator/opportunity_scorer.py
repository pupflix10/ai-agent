"""
AI Opportunity Evaluator & Scoring Engine
Evaluates market signals across 4 core dimensions:
1. Demand Volume Score
2. Supply / Competitor Weakness Gap Score
3. AI Solution Fit Score
4. 2-Year $10M+ ARR Scalability Potential Score

Keeps Immediate Alert Threshold at 8.5/10 as requested.
Strictly filters out random forum commentary, opinions, and tech news false positives.
"""

import json
import logging
import re
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class OpportunityScorer:
    def __init__(self):
        # Kept at 8.5 as requested by user
        self.immediate_alert_threshold = 8.5

    def is_random_commentary_or_discussion(self, text: str) -> bool:
        """Filter out general discussion, opinion posts, jokes, and tech news."""
        t = text.lower()

        # Random forum discussion / opinion patterns
        discussion_patterns = [
            r"stop listening to that", r"post never existed", r"made people less accurate",
            r"what do you do when", r"anatomy of a misfeature", r"how i learned",
            r"nvidia", r"cpu", r"gopro", r"roku", r"apple", r"sound card", r"bmw",
            r"infotainment", r"atari", r"gaming", r"beavis", r"kids act", r"police officer",
            r"outlook", r"grapheneos", r"django", r"decoupling capacitor", r"steam machine",
            r"stfu", r"passive income trap", r"fox to buy"
        ]
        return any(re.search(pat, t) for pat in discussion_patterns)

    def has_genuine_business_opportunity_intent(self, text: str) -> bool:
        """Check if signal describes a genuine business pain point or unmet software need."""
        t = text.lower()
        opportunity_signals = [
            r"paying \$", r"spending \$", r"costing \$", r"manual work", r"no software for",
            r"terrible tool", r"lack automation", r"struggling with audit", r"invoice matching",
            r"compliance gap", r"enterprise tool costs", r"need software to", r"looking for a tool",
            r"wish there was an app", r"why is there no tool"
        ]
        return any(re.search(pat, t) for pat in opportunity_signals)

    def evaluate_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a market signal and compute quantitative scalability and viability scores."""
        title = signal.get("title", "")
        desc = signal.get("description", "")
        combined = f"{title} {desc}".lower()

        # Discard random commentary, opinions, or tech news
        if self.is_random_commentary_or_discussion(combined):
            return self._build_filtered_result(signal, "Random Forum Commentary / Tech Discussion")

        # Must have genuine business opportunity intent
        if not self.has_genuine_business_opportunity_intent(combined):
            return self._build_filtered_result(signal, "Lacks Genuine Business Opportunity Intent")

        # 1. Demand Volume Score (0-10)
        demand_score = 7.0
        if any(w in combined for w in ["paying $", "costing $", "spending $", "high demand", "desperately need"]):
            demand_score = 9.5
        elif any(w in combined for w in ["manual work", "frustrating", "struggling with"]):
            demand_score = 8.5

        # 2. Supply Gap Score (0-10)
        supply_gap_score = 7.0
        if any(w in combined for w in ["no good software", "terrible tool", "lack automation", "expensive enterprise"]):
            supply_gap_score = 9.2
        elif any(w in combined for w in ["doing it manually", "outsourced"]):
            supply_gap_score = 8.2

        # 3. AI Solution Fit Score (0-10)
        ai_fit_score = 7.0
        if any(w in combined for w in ["compliance", "invoice", "audit", "automation", "document processing", "voice agent"]):
            ai_fit_score = 9.5
        elif any(w in combined for w in ["data", "software", "workflow"]):
            ai_fit_score = 8.2

        # 4. 2-Year $10M+ ARR Scalability Score (0-10)
        scalability_score = 7.0
        if any(w in combined for w in ["enterprise", "$10k", "$50k", "b2b", "compliance", "fintech"]):
            scalability_score = 9.2
        elif any(w in combined for w in ["smb", "agency", "subscription"]):
            scalability_score = 8.0

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
            "financial_projection": "$10M+ ARR Potential" if composite_score >= 8.5 else "$3M-$8M ARR",
            "build_effort": "Low-Medium (AI Agent System)",
            "is_immediate_alert": is_immediate,
            "suggested_mvp_concept": f"Build an automated AI workflow solution targeting {title[:40]}."
        }

    def _build_filtered_result(self, signal: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """Return a low-score result for non-business signals."""
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
        high_quality = [e for e in evaluated if e["scores"]["composite"] >= 7.0]
        high_quality.sort(key=lambda x: x["scores"]["composite"], reverse=True)
        return high_quality

if __name__ == "__main__":
    scorer = OpportunityScorer()
    sample = {
        "title": "Ask HN: What do you do when your AI agents are working?",
        "description": "Random commentary on AI agents",
        "source": "Hacker News"
    }
    res = scorer.evaluate_signal(sample)
    print(json.dumps(res, indent=2))
