"""
AI Opportunity Hunter Daemon & Orchestrator
Coordinates scraping, scoring, immediate email alerts, 48-hour digests, and Obsidian exports.
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from scrapers.multi_source_hunter import MarketHunter
from evaluator.opportunity_scorer import OpportunityScorer
from notifications.email_notifier import EmailNotifier
from exporters.obsidian_dossier import ObsidianDossierExporter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class OpportunityHunterDaemon:
    def __init__(self):
        self.hunter = MarketHunter()
        self.scorer = OpportunityScorer()
        self.notifier = EmailNotifier()
        self.obsidian = ObsidianDossierExporter()
        self.processed_urls = set()
        self.last_digest_time = datetime.now() - timedelta(hours=49)

    def run_hunt_cycle(self) -> Dict[str, Any]:
        """Execute a full market hunt cycle."""
        logger.info("--- STARTING MARKET HUNT CYCLE ---")
        raw_signals = self.hunter.hunt_all_opportunities()
        new_signals = [s for s in raw_signals if s.get("url") not in self.processed_urls]
        logger.info(f"Identified {len(new_signals)} new market signals to evaluate.")

        scored_opportunities = self.scorer.evaluate_batch(new_signals)

        immediate_alerts_sent = 0
        dossiers_created = 0

        for opp in scored_opportunities:
            url = opp.get("url")
            if url:
                self.processed_urls.add(url)

            filepath = self.obsidian.export_dossier(opp)
            dossiers_created += 1

            if opp.get("is_immediate_alert"):
                logger.info(f"🔥 Immediate Alert! Score: {opp['scores']['composite']} - {opp['title']}")
                self.notifier.send_immediate_alert(opp)
                immediate_alerts_sent += 1

        now = datetime.now()
        digest_sent = False
        if (now - self.last_digest_time) >= timedelta(hours=48):
            logger.info("📬 48-Hour Digest Period Elapsed. Sending Email Digest...")
            self.notifier.send_bidaily_digest(scored_opportunities)
            self.last_digest_time = now
            digest_sent = True

        logger.info(f"--- CYCLE COMPLETE: {len(scored_opportunities)} scored, {immediate_alerts_sent} alerts sent, {dossiers_created} dossiers created ---")
        return {
            "total_evaluated": len(scored_opportunities),
            "immediate_alerts_sent": immediate_alerts_sent,
            "dossiers_created": dossiers_created,
            "digest_sent": digest_sent,
            "top_opportunity": scored_opportunities[0] if scored_opportunities else None
        }

if __name__ == "__main__":
    daemon = OpportunityHunterDaemon()
    result = daemon.run_hunt_cycle()
    print(json.dumps(result, indent=2, default=str))
