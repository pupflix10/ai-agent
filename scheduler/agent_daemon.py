"""
AI Opportunity Hunter Agent Daemon & Orchestrator
Coordinates scraping, evaluation, immediate email alerts, 48-hour digests, and Obsidian exports.
Includes strict persistent deduplication (processed_history.json) to prevent repeating alerts.
"""

import time
import json
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from scrapers.multi_source_hunter import MarketHunter
from evaluator.opportunity_scorer import OpportunityScorer
from notifications.email_notifier import EmailNotifier
from exporters.obsidian_dossier import ObsidianDossierExporter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "processed_history.json")

class OpportunityHunterDaemon:
    def __init__(self):
        self.hunter = MarketHunter()
        self.scorer = OpportunityScorer()
        self.notifier = EmailNotifier()
        self.obsidian = ObsidianDossierExporter()
        self.history = self._load_history()
        self.last_digest_time = datetime.now() - timedelta(hours=49)

    def _load_history(self) -> Dict[str, Any]:
        """Load persistent history of sent alerts to prevent duplicate emails."""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load history file: {e}")
        return {"sent_alerts": [], "processed_urls": [], "last_digest": None}

    def _save_history(self):
        """Save persistent history to disk."""
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save history file: {e}")

    def run_hunt_cycle(self) -> Dict[str, Any]:
        """Execute a full market hunt cycle with strict deduplication."""
        logger.info("--- STARTING MARKET HUNT CYCLE ---")
        raw_signals = self.hunter.hunt_all_opportunities()
        
        sent_alerts_set = set(self.history.get("sent_alerts", []))
        processed_urls_set = set(self.history.get("processed_urls", []))

        # Filter out already processed signals
        new_signals = [
            s for s in raw_signals 
            if s.get("url") not in processed_urls_set and s.get("title") not in sent_alerts_set
        ]
        logger.info(f"Identified {len(new_signals)} fresh, un-alerted market signals to evaluate.")

        if not new_signals:
            logger.info("No new market signals found this run. Skipping email dispatch to prevent spam.")
            return {
                "total_evaluated": 0,
                "immediate_alerts_sent": 0,
                "dossiers_created": 0,
                "digest_sent": False,
                "top_opportunity": None
            }

        scored_opportunities = self.scorer.evaluate_batch(new_signals)

        immediate_alerts_sent = 0
        dossiers_created = 0

        for opp in scored_opportunities:
            title = opp.get("title")
            url = opp.get("url")

            # Track URL as processed
            if url and url not in processed_urls_set:
                processed_urls_set.add(url)
                self.history["processed_urls"].append(url)

            # Check if alert was already sent for this exact title
            if title in sent_alerts_set:
                logger.info(f"Skipping duplicate alert for already sent title: {title}")
                continue

            # Save dossier
            filepath = self.obsidian.export_dossier(opp)
            dossiers_created += 1

            # Dispatch immediate alert if score >= 8.5 AND not sent before
            if opp.get("is_immediate_alert"):
                logger.info(f"🔥 New Immediate Alert! Score: {opp['scores']['composite']} - {title}")
                success = self.notifier.send_immediate_alert(opp)
                if success:
                    sent_alerts_set.add(title)
                    self.history["sent_alerts"].append(title)
                    immediate_alerts_sent += 1

        # Check 48-hour scheduled digest
        now = datetime.now()
        digest_sent = False
        last_digest_str = self.history.get("last_digest")
        should_send_digest = True
        
        if last_digest_str:
            try:
                last_dt = datetime.fromisoformat(last_digest_str)
                if (now - last_dt) < timedelta(hours=48):
                    should_send_digest = False
            except Exception:
                pass

        # Only send digest if there are actual NEW scored opportunities
        if should_send_digest and scored_opportunities:
            logger.info("📬 48-Hour Digest Period Elapsed. Sending Email Digest for new opportunities...")
            digest_success = self.notifier.send_bidaily_digest(scored_opportunities)
            if digest_success:
                self.history["last_digest"] = now.isoformat()
                digest_sent = True

        self._save_history()
        logger.info(f"--- CYCLE COMPLETE: {len(scored_opportunities)} scored, {immediate_alerts_sent} new alerts sent, {dossiers_created} dossiers created ---")

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
