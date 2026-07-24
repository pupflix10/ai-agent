#!/usr/bin/env python3
"""
AI Business Opportunity Hunter Agent — Main CLI Entry Point
Email notifications via Gmail SMTP (Zero 3rd-Party APIs)
"""

import sys
import json
import os
import subprocess
import argparse

# Load .env file manually if present
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

from scheduler.agent_daemon import OpportunityHunterDaemon
from notifications.email_notifier import EmailNotifier

PLIST_PATH = os.path.expanduser("~/Library/LaunchAgents/com.aiagent.opportunityhunter.plist")

def check_agent_status():
    """Check if the background LaunchAgent is active."""
    res = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
    is_running = "com.aiagent.opportunityhunter" in res.stdout
    
    print("\n================ 🎛️ AI AGENT FLEET STATUS ================")
    print("Agent Name                 | Status     | Schedule      | Target")
    print("-------------------------------------------------------------------")
    status_str = "🟢 RUNNING" if is_running else "🔴 STOPPED"
    print(f"01. Opportunity Hunter     | {status_str}  | Every 12 hrs  | Email & Obsidian")
    print("============================================================\n")
    print("To stop background agent:  python3 main.py --stop")
    print("To start background agent: python3 main.py --start")
    print("To view Obsidian dashboard: Check '02 My Businesses/00 - AI Agent Control Center.md'\n")

def stop_agent():
    """Stop/Unload the background agent."""
    if os.path.exists(PLIST_PATH):
        subprocess.run(["launchctl", "unload", PLIST_PATH], check=False)
        print("🛑 Background AI Opportunity Hunter Agent has been STOPPED.")
    else:
        print("Agent plist not found.")

def start_agent():
    """Start/Load the background agent."""
    if os.path.exists(PLIST_PATH):
        subprocess.run(["launchctl", "load", PLIST_PATH], check=False)
        print("🟢 Background AI Opportunity Hunter Agent is now STARTED & ACTIVE.")
    else:
        print("Agent plist not found.")

def main():
    parser = argparse.ArgumentParser(description="AI Business Opportunity Hunter Agent ($10M+ ARR Target)")
    parser.add_argument("--scan", action="store_true", help="Run full market opportunity hunt and scoring cycle")
    parser.add_argument("--status", action="store_true", help="Check status of all AI Agents")
    parser.add_argument("--stop", action="store_true", help="Stop the background AI Agent")
    parser.add_argument("--start", action="store_true", help="Start the background AI Agent")
    parser.add_argument("--test-email", action="store_true", help="Send a test email notification")
    args = parser.parse_args()

    if args.status:
        check_agent_status()
        return

    if args.stop:
        stop_agent()
        return

    if args.start:
        start_agent()
        return

    if args.test_email:
        notifier = EmailNotifier()
        sample_opp = {
            "title": "Automated Cross-Platform Regulatory Compliance Auditor for AI Native Startups",
            "description": "High demand among EU & US fintech/healthtech startups struggling with manual EU AI Act & HIPAA audit preparation. Current enterprise tools cost $50k+/year.",
            "financial_projection": "$10M - $25M ARR in 24 months",
            "build_effort": "Low-Medium (AI Agent Orchestration + Integrations)",
            "source": "G2 Reviews & Upwork Request Data",
            "scores": {"composite": 9.27},
            "suggested_mvp_concept": "Build an Agentic Compliance Auditor that connects to GitHub, AWS/GCP, and PostgreSQL to continuously generate EU AI Act audit reports automatically."
        }
        print("🚀 Sending Test Email Alert...")
        success = notifier.send_immediate_alert(sample_opp)
        if success:
            print("✅ Test email sent successfully!")
        return

    # Default action: run full hunt cycle
    print("🚀 Initializing AI Business Opportunity Hunter Agent...")
    daemon = OpportunityHunterDaemon()
    results = daemon.run_hunt_cycle()

    top = results.get("top_opportunity")
    print("\n✅ HUNT CYCLE COMPLETED SUCCESSFULLY!")
    print(f"• Total Opportunities Evaluated: {results['total_evaluated']}")
    print(f"• Immediate Email Alerts Sent: {results['immediate_alerts_sent']}")
    print(f"• Obsidian Dossiers Exported: {results['dossiers_created']}")

    if top:
        print("\n🔥 TOP DISCOVERED OPPORTUNITY:")
        print(f"Title: {top['title']}")
        print(f"Score: {top['scores']['composite']}/10")
        print(f"Potential: {top['financial_projection']}")

if __name__ == "__main__":
    main()
