"""
Unit Test Suite for Phase 2 Enrichment Agent.
Tests email scraping & pattern guessing, ad signal detection, priority score calculation, and file outputs.
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from lead_pipeline.enrichment_agent import EnrichmentAgent

class TestPhase2EnrichmentAgent(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cache_file = os.path.join(self.temp_dir, "test_cache.json")
        self.csv_file = os.path.join(self.temp_dir, "test_leads.csv")

        self.patcher1 = patch("lead_pipeline.sheets_exporter.CACHE_FILE", self.cache_file)
        self.patcher2 = patch("lead_pipeline.sheets_exporter.CSV_EXPORT_PATH", self.csv_file)
        self.patcher3 = patch("lead_pipeline.enrichment_agent.CACHE_FILE", self.cache_file)
        self.patcher4 = patch("lead_pipeline.enrichment_agent.CSV_EXPORT_PATH", self.csv_file)
        self.patcher5 = patch("lead_pipeline.enrichment_agent.SCREENSHOTS_DIR", os.path.join(self.temp_dir, "screenshots"))
        
        self.patcher1.start()
        self.patcher2.start()
        self.patcher3.start()
        self.patcher4.start()
        self.patcher5.start()

        self.agent = EnrichmentAgent()

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher3.stop()
        self.patcher4.stop()
        self.patcher5.stop()
        shutil.rmtree(self.temp_dir)

    def test_priority_score_logic(self):
        # High Priority: running_ads == 'yes', pagespeed < 50, reviews >= 20
        high = self.agent.calculate_priority_score(running_ads="yes", pagespeed_score=35, review_count=25)
        self.assertEqual(high, "high")

        # Medium Priority: only one or two signals present
        med1 = self.agent.calculate_priority_score(running_ads="no", pagespeed_score=35, review_count=25)
        self.assertEqual(med1, "medium")

        med2 = self.agent.calculate_priority_score(running_ads="yes", pagespeed_score=65, review_count=5)
        self.assertEqual(med2, "medium")

        # Low Priority: no signals present (ads = no, pagespeed >= 50, reviews < 20)
        low = self.agent.calculate_priority_score(running_ads="no", pagespeed_score=75, review_count=8)
        self.assertEqual(low, "low")

    def test_email_scraping_and_fallback(self):
        # Test fallback guessing logic
        email, email_type = self.agent.scrape_and_find_email("http://www.nonexistentdomain12345.com.au")
        self.assertEqual(email, "info@nonexistentdomain12345.com.au")
        self.assertEqual(email_type, "guessed")

    def test_enrich_lead_end_to_end(self):
        lead = {
            "business_name": "Sydney Quality Plumbing",
            "phone": "0299991111",
            "website_url": "http://www.sydneyqualityplumbing.com.au",
            "city": "Sydney, NSW",
            "category": "Plumbing",
            "rating": 4.7,
            "review_count": 30,
            "pagespeed_score": 38,
            "date_found": "2026-07-25",
            "place_id": "place_au_p1",
            "status": "qualified_weak_site"
        }

        enriched = self.agent.enrich_lead(lead)
        self.assertEqual(enriched["status"], "enriched")
        self.assertIn("email", enriched)
        self.assertIn(enriched["email_type"], ["confirmed", "guessed"])
        self.assertIn(enriched["priority_score"], ["high", "medium", "low"])
        self.assertTrue(os.path.exists(enriched["screenshot_path"]))

if __name__ == "__main__":
    unittest.main()
