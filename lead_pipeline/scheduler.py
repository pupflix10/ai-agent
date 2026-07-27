"""
Scheduler helper for weekly automated runs of Phase 1 Prospect Finder Agent.
Supports execution via CLI, launchd daemon, or cron.
"""

import os
import sys
import logging
from lead_pipeline.prospect_finder import ProspectFinderAgent
from lead_pipeline.config import LOG_FILE

logger = logging.getLogger("scheduler")

def run_scheduled_job():
    """Weekly scheduled job entry point."""
    print("⏰ [SCHEDULER] Triggering Phase 1 Weekly Prospect Finder Job...")
    try:
        agent = ProspectFinderAgent()
        added = agent.run_pipeline()
        print(f"✅ [SCHEDULER] Weekly job completed successfully. {added} new qualified leads saved.")
    except Exception as e:
        print(f"❌ [SCHEDULER] Job failed with error: {e}")
        logger.error(f"Scheduled job exception: {e}")

if __name__ == "__main__":
    run_scheduled_job()
