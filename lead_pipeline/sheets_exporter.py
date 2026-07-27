"""
Google Sheets Exporter and Deduplication Engine for Prospect Leads.
Supports Google Sheets API (via gspread or urllib) and local CSV/JSON cache fallback.
"""

import os
import json
import csv
import logging
from datetime import datetime
from typing import List, Dict, Any, Set
from urllib.parse import urlparse

from lead_pipeline.config import (
    DATA_DIR, CACHE_FILE, CSV_EXPORT_PATH, GOOGLE_SHEET_ID, GOOGLE_SERVICE_ACCOUNT_FILE, LOG_FILE
)

# Setup logger
os.makedirs(DATA_DIR, exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("sheets_exporter")

CSV_HEADERS = [
    "business_name",
    "phone",
    "website_url",
    "city",
    "category",
    "rating",
    "review_count",
    "pagespeed_score",
    "date_found",
    "place_id",
    "status"
]

def normalize_domain(url: str) -> str:
    """Extract clean domain name from website URL for deduplication."""
    if not url:
        return ""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return url.lower()

class LeadStorageEngine:
    def __init__(self):
        self.cache_file = CACHE_FILE
        self.csv_file = CSV_EXPORT_PATH
        self.processed_keys: Set[str] = set()
        self.processed_leads: List[Dict[str, Any]] = []
        self._load_cache()

    def _load_cache(self):
        """Load deduplication key index from cache file and CSV if present."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    data = json.load(f)
                    self.processed_leads = data.get("leads", [])
                    for item in self.processed_leads:
                        if item.get("place_id"):
                            self.processed_keys.add(f"place:{item['place_id']}")
                        if item.get("website_url"):
                            dom = normalize_domain(item["website_url"])
                            if dom:
                                self.processed_keys.add(f"domain:{dom}")
                        if item.get("phone"):
                            self.processed_keys.add(f"phone:{item['phone']}")
            except Exception as e:
                logger.error(f"Error loading lead cache: {e}")

        # Also load from existing CSV if present
        if os.path.exists(self.csv_file):
            try:
                with open(self.csv_file, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get("place_id"):
                            self.processed_keys.add(f"place:{row['place_id']}")
                        if row.get("website_url"):
                            dom = normalize_domain(row["website_url"])
                            if dom:
                                self.processed_keys.add(f"domain:{dom}")
                        if row.get("phone"):
                            self.processed_keys.add(f"phone:{row['phone']}")
            except Exception as e:
                logger.error(f"Error reading CSV file for deduplication: {e}")

    def is_duplicate(self, lead: Dict[str, Any]) -> bool:
        """Check if lead has already been processed using place_id, domain, or phone."""
        place_id = lead.get("place_id")
        if place_id and f"place:{place_id}" in self.processed_keys:
            return True

        url = lead.get("website_url")
        if url:
            dom = normalize_domain(url)
            if dom and f"domain:{dom}" in self.processed_keys:
                return True

        phone = lead.get("phone")
        if phone and f"phone:{phone}" in self.processed_keys:
            return True

        return False

    def save_leads(self, new_leads: List[Dict[str, Any]]) -> int:
        """Filter out duplicates and append new leads to JSON cache, CSV, and Google Sheets."""
        unique_leads = []
        for lead in new_leads:
            if not self.is_duplicate(lead):
                unique_leads.append(lead)
                # Register keys
                if lead.get("place_id"):
                    self.processed_keys.add(f"place:{lead['place_id']}")
                if lead.get("website_url"):
                    dom = normalize_domain(lead["website_url"])
                    if dom:
                        self.processed_keys.add(f"domain:{dom}")
                if lead.get("phone"):
                    self.processed_keys.add(f"phone:{lead['phone']}")
            else:
                logger.info(f"Skipping duplicate lead: {lead.get('business_name')} ({lead.get('website_url')})")

        if not unique_leads:
            logger.info("No new unique leads to save.")
            return 0

        # Save to local CSV
        file_exists = os.path.exists(self.csv_file)
        with open(self.csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            if not file_exists:
                writer.writeheader()
            for lead in unique_leads:
                row = {k: lead.get(k, "") for k in CSV_HEADERS}
                writer.writerow(row)

        # Save to local JSON cache
        self.processed_leads.extend(unique_leads)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump({"leads": self.processed_leads, "last_updated": datetime.now().isoformat()}, f, indent=2)

        # Try Google Sheets Export if gspread is installed and credentials exist
        self._export_to_google_sheets(unique_leads)

        logger.info(f"Successfully saved {len(unique_leads)} new unique leads.")
        return len(unique_leads)

    def _export_to_google_sheets(self, leads: List[Dict[str, Any]]):
        """Attempt Google Sheets update via gspread if configured."""
        if not GOOGLE_SHEET_ID:
            logger.info("GOOGLE_SHEET_ID not configured; skipping direct Google Sheets upload.")
            return

        try:
            import gspread
            if os.path.exists(GOOGLE_SERVICE_ACCOUNT_FILE):
                gc = gspread.service_account(filename=GOOGLE_SERVICE_ACCOUNT_FILE)
                sh = gc.open_by_key(GOOGLE_SHEET_ID)
                worksheet = sh.sheet1
                
                # Check headers
                existing = worksheet.get_all_values()
                if not existing:
                    worksheet.append_row(CSV_HEADERS)

                rows_to_append = []
                for lead in leads:
                    rows_to_append.append([str(lead.get(k, "")) for k in CSV_HEADERS])

                worksheet.append_rows(rows_to_append)
                logger.info(f"Uploaded {len(leads)} rows to Google Sheet ID {GOOGLE_SHEET_ID}.")
            else:
                logger.warning(f"Google service account file {GOOGLE_SERVICE_ACCOUNT_FILE} not found.")
        except ImportError:
            logger.info("gspread library not installed. Using local CSV output.")
        except Exception as e:
            logger.error(f"Failed to update Google Sheet: {e}")
