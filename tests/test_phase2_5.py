"""
Unit Test Suite for Phase 2.5 Spec Site Generator.
Tests trade template selection, name length overflow handling, HTML output, and preview readiness.
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from lead_pipeline.spec_site_generator import SpecSiteGeneratorAgent

class TestPhase25SpecSiteGenerator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.previews_dir = os.path.join(self.temp_dir, "previews")
        self.csv_file = os.path.join(self.temp_dir, "test_leads.csv")

        self.patcher1 = patch("lead_pipeline.spec_site_generator.PREVIEWS_DIR", self.previews_dir)
        self.patcher2 = patch("lead_pipeline.spec_site_generator.CSV_EXPORT_PATH", self.csv_file)
        self.patcher1.start()
        self.patcher2.start()

        self.generator = SpecSiteGeneratorAgent()

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        shutil.rmtree(self.temp_dir)

    def test_validation_overflow_name(self):
        long_name_lead = {
            "business_name": "A" * 70,  # 70 chars > 65 max
            "phone": "02 9123 4567",
            "city": "Sydney, NSW",
            "category": "HVAC"
        }
        valid, err = self.generator.validate_lead_data(long_name_lead)
        self.assertFalse(valid)
        self.assertIn("too long", err)

    def test_successful_spec_site_generation(self):
        lead = {
            "business_name": "Sydney Premium HVAC Services",
            "phone": "02 9123 4567",
            "city": "Sydney, NSW",
            "category": "HVAC",
            "priority_score": "high",
            "status": "enriched"
        }
        success, url, updated_lead = self.generator.generate_spec_site(lead)
        self.assertTrue(success)
        self.assertEqual(updated_lead["status"], "preview ready — pending QA")
        self.assertTrue(os.path.exists(updated_lead["preview_path"]))
        
        # Verify generated HTML contents
        with open(updated_lead["preview_path"], "r") as f:
            html = f.read()
            self.assertIn("Sydney Premium HVAC Services", html)
            self.assertIn("02 9123 4567", html)
            self.assertIn("Sydney, NSW", html)

if __name__ == "__main__":
    unittest.main()
