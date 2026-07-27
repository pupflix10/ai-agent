"""
Configuration settings for Australia Lead Generation Pipeline.
"""

import os

# Load .env variables if present
def load_env():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_file = os.path.join(base_dir, ".env")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env()

# API Keys & Settings
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
GOOGLE_PAGESPEED_API_KEY = os.getenv("GOOGLE_PAGESPEED_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")

# Target Geography
DEFAULT_COUNTRY_CODE = "AU"

DEFAULT_TARGET_CITIES = [
    "Sydney, NSW",
    "Melbourne, VIC",
    "Brisbane, QLD",
    "Perth, WA",
    "Adelaide, SA",
    "Gold Coast, QLD",
    "Canberra, ACT",
    "Newcastle, NSW"
]

DEFAULT_TRADE_CATEGORIES = [
    "HVAC",
    "Air Conditioning Repair",
    "Plumbing",
    "Roofing",
    "Electrician"
]

# Prospect Qualification Thresholds
MIN_REVIEW_COUNT = 10
MAX_PAGESPEED_SCORE = 50  # Mobile Lighthouse performance score out of 100

# File Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_FILE = os.path.join(DATA_DIR, "processed_leads.json")
CSV_EXPORT_PATH = os.path.join(DATA_DIR, "prospects_leads.csv")
LOG_FILE = os.path.join(DATA_DIR, "lead_pipeline.log")
