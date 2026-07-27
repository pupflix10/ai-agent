"""
Unit Test Suite for Phase 2.75 QA Checkpoint Agent.
Tests approval/rejection workflows, status changes, and failure reason logging.
"""

import os
import csv
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch

from lead_pipeline.qa_checkpoint import QACheckpointAgent

class TestPhase275QACheckpoint(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.csv_file = os.path.join(self.temp_dir, "test_leads.csv")
        self.failure_file = os.path.join(self.temp_dir, "failure_log.json")

        self.patcher1 = patch("lead_pipeline.qa_checkpoint.CSV_EXPORT_PATH", self.csv_file)
        self.patcher2 = patch("lead_pipeline.qa_checkpoint.FAILURE_LOG_FILE", self.failure_file)
        self.patcher1.start()
        self.patcher2.start()

        # Seed test CSV
        headers = [
            "business_name", "phone", "website_url", "city", "category",
            "rating", "review_count", "pagespeed_score", "date_found",
            "place_id", "email", "email_type", "running_ads",
            "screenshot_path", "priority_score", "preview_url", "preview_path",
            "generation_error", "status"
        ]
        rows = [
            {
                "business_name": "Test HVAC 1",
                "place_id": "p101",
                "status": "preview ready — pending QA"
            },
            {
                "business_name": "Test HVAC 2",
                "place_id": "p102",
                "status": "preview ready — pending QA"
            }
        ]
        with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)

        self.agent = QACheckpointAgent()

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        shutil.rmtree(self.temp_dir)

    def test_get_pending_qa_leads(self):
        pending = self.agent.get_pending_qa_leads()
        self.assertEqual(len(pending), 2)

    def test_approve_lead(self):
        res = self.agent.approve_lead("p101")
        self.assertTrue(res)
        pending = self.agent.get_pending_qa_leads()
        self.assertEqual(len(pending), 1)

    def test_reject_lead(self):
        res = self.agent.reject_lead("p102", "broken layout overflow")
        self.assertTrue(res)
        
        # Check failure log
        with open(self.failure_file, "r") as f:
            log_data = json.load(f)
            self.assertEqual(len(log_data), 1)
            self.assertEqual(log_data[0]["reason"], "broken layout overflow")

if __name__ == "__main__":
    unittest.main()
