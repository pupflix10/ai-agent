"""
Unit and Integration Test Suite for Phase 1 Prospect Finder Agent.
Tests Places API filtering, review count, website checking, PageSpeed thresholding, deduplication, and file exports.
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from lead_pipeline.config import MIN_REVIEW_COUNT, MAX_PAGESPEED_SCORE
from lead_pipeline.sheets_exporter import LeadStorageEngine, normalize_domain
from lead_pipeline.prospect_finder import ProspectFinderAgent

class TestPhase1ProspectFinder(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cache_file = os.path.join(self.temp_dir, "test_cache.json")
        self.csv_file = os.path.join(self.temp_dir, "test_leads.csv")
        
        # Patch config paths to use temp directory
        self.patcher1 = patch("lead_pipeline.sheets_exporter.CACHE_FILE", self.cache_file)
        self.patcher2 = patch("lead_pipeline.sheets_exporter.CSV_EXPORT_PATH", self.csv_file)
        self.patcher3 = patch("lead_pipeline.sheets_exporter.DATA_DIR", self.temp_dir)
        self.patcher1.start()
        self.patcher2.start()
        self.patcher3.start()

        self.storage = LeadStorageEngine()

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher3.stop()
        shutil.rmtree(self.temp_dir)

    def test_normalize_domain(self):
        self.assertEqual(normalize_domain("http://www.sydneyhvac.com.au/about"), "sydneyhvac.com.au")
        self.assertEqual(normalize_domain("https://melbourneplumbing.com/"), "melbourneplumbing.com")
        self.assertEqual(normalize_domain("brisbaneroofing.com.au"), "brisbaneroofing.com.au")

    def test_deduplication(self):
        lead1 = {
            "place_id": "ChIJ12345",
            "business_name": "Sydney Air Con Specialists",
            "phone": "0299998888",
            "website_url": "http://sydneyaircon.com.au",
            "city": "Sydney, NSW",
            "category": "HVAC",
            "rating": 4.5,
            "review_count": 15,
            "pagespeed_score": 38,
            "date_found": "2026-07-25",
            "status": "qualified_weak_site"
        }

        # Save lead1
        saved = self.storage.save_leads([lead1])
        self.assertEqual(saved, 1)

        # Check duplicate by place_id
        self.assertTrue(self.storage.is_duplicate({"place_id": "ChIJ12345"}))

        # Check duplicate by domain
        self.assertTrue(self.storage.is_duplicate({"website_url": "https://www.sydneyaircon.com.au/contact"}))

        # Check duplicate by phone
        self.assertTrue(self.storage.is_duplicate({"phone": "0299998888"}))

        # Attempt to save duplicate again -> should return 0 saved
        saved_dup = self.storage.save_leads([lead1])
        self.assertEqual(saved_dup, 0)

    def test_filter_and_qualify_prospects(self):
        agent = ProspectFinderAgent(places_api_key="mock", pagespeed_api_key="mock")
        agent.storage = self.storage

        mock_raw = [
            {
                "place_id": "p1",
                "business_name": "Small HVAC",
                "review_count": 5,  # < 10 reviews -> Should be filtered out
                "website_url": "http://smallhvac.com.au",
                "city": "Sydney, NSW",
                "category": "HVAC"
            },
            {
                "place_id": "p2",
                "business_name": "No Website Plumbing",
                "review_count": 25,
                "website_url": "",  # No website -> Should be filtered out
                "city": "Sydney, NSW",
                "category": "Plumbing"
            },
            {
                "place_id": "p3",
                "business_name": "Fast Site Roofing",
                "review_count": 30,
                "website_url": "http://fastroofing.com.au",
                "city": "Sydney, NSW",
                "category": "Roofing"
            },
            {
                "place_id": "p4",
                "business_name": "Target Slow HVAC",
                "review_count": 42,
                "website_url": "http://targetslowhvac.com.au",
                "city": "Sydney, NSW",
                "category": "HVAC"
            }
        ]

        # Mock PageSpeed scores:
        # Fast site -> 85 (>= 50, filtered out)
        # Target site -> 32 (< 50, qualified!)
        def mock_pagespeed(url, **kwargs):
            if "fastroofing" in url:
                return 85
            if "targetslowhvac" in url:
                return 32
            return 90

        with patch.object(agent, "fetch_pagespeed_score", side_effect=mock_pagespeed):
            qualified = agent.filter_and_qualify_prospects(mock_raw)
            
            # Only p4 should qualify
            self.assertEqual(len(qualified), 1)
            self.assertEqual(qualified[0]["business_name"], "Target Slow HVAC")
            self.assertEqual(qualified[0]["pagespeed_score"], 32)
            self.assertEqual(qualified[0]["status"], "qualified_weak_site")

if __name__ == "__main__":
    unittest.main()
