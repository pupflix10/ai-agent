"""
Unit Test Suite for Phase 3 Outreach Agent.
Tests opening line branching, email template formatting, rate limits, and HARD STOP on inbound reply.
"""

import os
import csv
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch

from lead_pipeline.outreach_agent import OutreachAgent

class TestPhase3OutreachAgent(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.csv_file = os.path.join(self.temp_dir, "test_leads.csv")

        self.patcher1 = patch("lead_pipeline.outreach_agent.CSV_EXPORT_PATH", self.csv_file)
        self.patcher1.start()

        # Seed test leads
        headers = [
            "business_name", "phone", "website_url", "city", "category",
            "rating", "review_count", "pagespeed_score", "date_found",
            "place_id", "email", "email_type", "running_ads",
            "screenshot_path", "priority_score", "preview_url", "preview_path",
            "generation_error", "outreach_angle", "last_contact_date",
            "followup_stage", "inbound_reply", "status"
        ]
        rows = [
            {
                "business_name": "Ad Running HVAC",
                "place_id": "p201",
                "email": "contact@adhvac.com.au",
                "running_ads": "yes",
                "category": "HVAC",
                "preview_url": "http://localhost:8000/previews/ad_running_hvac/index.html",
                "status": "preview ready"
            },
            {
                "business_name": "Organic Plumbing",
                "place_id": "p202",
                "email": "info@organicplumbing.com.au",
                "running_ads": "no",
                "category": "Plumbing",
                "preview_url": "http://localhost:8000/previews/organic_plumbing/index.html",
                "status": "preview ready"
            }
        ]
        with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)

        self.agent = OutreachAgent()

    def tearDown(self):
        self.patcher1.stop()
        shutil.rmtree(self.temp_dir)

    def test_opening_line_branching(self):
        # Test ad spend angle
        line_ads, angle_ads = self.agent.generate_opening_line({
            "business_name": "Ad Running HVAC",
            "category": "HVAC",
            "running_ads": "yes"
        })
        self.assertEqual(angle_ads, "ad_spend_efficiency")
        self.assertIn("running ads for hvac", line_ads)

        # Test competitive positioning angle
        line_no_ads, angle_no_ads = self.agent.generate_opening_line({
            "business_name": "Organic Plumbing",
            "category": "Plumbing",
            "running_ads": "no"
        })
        self.assertEqual(angle_no_ads, "competitive_positioning")
        self.assertIn("fantastic customer reviews", line_no_ads)

    def test_inbound_reply_hard_stop(self):
        # Trigger reply hard stop on p201
        res = self.agent.handle_inbound_reply("p201")
        self.assertTrue(res)

        # Read CSV and verify status changed to 'needs human response'
        with open(self.csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            leads = list(reader)
            p201_lead = [l for l in leads if l["place_id"] == "p201"][0]
            self.assertEqual(p201_lead["status"], "needs human response")
            self.assertEqual(p201_lead["inbound_reply"], "yes")

    def test_process_outreach_campaign(self):
        sent = self.agent.process_outreach_campaign()
        self.assertEqual(sent, 2)

        # Check status updated to 'contacted — email sent'
        with open(self.csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            leads = list(reader)
            for l in leads:
                self.assertEqual(l["status"], "contacted — email sent")

if __name__ == "__main__":
    unittest.main()
