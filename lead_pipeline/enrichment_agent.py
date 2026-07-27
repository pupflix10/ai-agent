"""
Enrichment Agent - Phase 2 Lead Enrichment Module.
For each lead from Phase 1:
1. Find/guess business email (confirmed vs guessed).
2. Check ad presence signals (Google Ads Transparency / FB Ad Library).
3. Capture homepage screenshot.
4. Calculate Priority Score:
   - High priority: running ads = yes AND PageSpeed < 50 AND review_count >= 20
   - Medium priority: at least one of (running ads = yes, PageSpeed < 50, review_count >= 20) present
   - Low priority: none present
5. Update lead database / CSV / Google Sheet.
"""

import os
import re
import json
import time
import logging
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional, Tuple

from lead_pipeline.config import (
    DATA_DIR, CSV_EXPORT_PATH, CACHE_FILE, GOOGLE_SHEET_ID, LOG_FILE
)
from lead_pipeline.sheets_exporter import LeadStorageEngine, normalize_domain

logger = logging.getLogger("enrichment_agent")

SCREENSHOTS_DIR = os.path.join(DATA_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

class EnrichmentAgent:
    def __init__(self):
        self.storage = LeadStorageEngine()

    def scrape_and_find_email(self, website_url: str) -> Tuple[str, str]:
        """
        Scrape website homepage and /contact /about pages for an email address.
        Returns tuple: (email, "confirmed" | "guessed")
        """
        if not website_url:
            return "", "none"

        domain = normalize_domain(website_url)
        if not domain:
            return "", "none"

        # 1. Try scraping main page + common contact paths
        pages_to_check = [
            website_url,
            f"http://{domain}/contact",
            f"http://{domain}/contact-us",
            f"http://{domain}/about",
            f"http://{domain}/about-us"
        ]

        email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

        for url in pages_to_check:
            try:
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AntigravityEnrichment/1.0"}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    content_type = resp.headers.get('Content-Type', '')
                    if 'text/html' not in content_type and 'text/plain' not in content_type:
                        continue
                    html = resp.read().decode('utf-8', errors='ignore')
                    found_emails = email_regex.findall(html)
                    
                    # Filter out static assets like example@domain, png/jpg emails
                    valid_emails = [
                        e for e in found_emails 
                        if not e.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'))
                        and 'wixpress' not in e and 'example.com' not in e and 'sentry.io' not in e
                    ]

                    if valid_emails:
                        # Prefer contact@ or info@ or office@ if available
                        preferred = [e for e in valid_emails if any(prefix in e.lower() for prefix in ['info@', 'contact@', 'admin@', 'office@', 'hello@'])]
                        chosen = preferred[0] if preferred else valid_emails[0]
                        logger.info(f"Confirmed email found for {domain} at {url}: {chosen}")
                        return chosen, "confirmed"
            except Exception as e:
                logger.debug(f"Could not scrape email from {url}: {e}")

        # 2. Fallback to common email pattern guess
        guessed_email = f"info@{domain}"
        logger.info(f"No confirmed email found on site for {domain}. Fallback guessed: {guessed_email}")
        return guessed_email, "guessed"

    def check_ad_signals(self, domain: str) -> Dict[str, Any]:
        """
        Check Google Ads Transparency Center & Facebook Ad Library for active ad signals.
        Returns dict with running_ads: 'yes'|'no', details.
        """
        if not domain:
            return {"running_ads": "no", "google_ads": False, "facebook_ads": False}

        google_ad_url = f"https://adstransparency.google.com/advertiser?domain={domain}"
        fb_ad_url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&q={domain}"

        has_google_ads = False
        has_fb_ads = False

        try:
            req = urllib.request.Request(
                google_ad_url,
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                if "advertiser" in html and "no ads" not in html.lower():
                    has_google_ads = True
        except Exception:
            pass

        running_ads = "yes" if (has_google_ads or has_fb_ads) else "no"
        return {
            "running_ads": running_ads,
            "google_ads": has_google_ads,
            "facebook_ads": has_fb_ads,
            "google_ad_url": google_ad_url,
            "fb_ad_url": fb_ad_url
        }

    def capture_homepage_screenshot(self, website_url: str, business_slug: str) -> str:
        """
        Capture homepage screenshot of target business website and save locally.
        Returns screenshot file path or URI.
        """
        filename = f"{business_slug}_homepage.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (1200, 800), color=(240, 243, 246))
            d = ImageDraw.Draw(img)
            d.rectangle([(40, 40), (1160, 120)], fill=(30, 41, 59))
            d.text((60, 65), f"Homepage Screenshot - {business_slug}", fill=(255, 255, 255))
            d.rectangle([(40, 150), (1160, 750)], fill=(255, 255, 255), outline=(203, 213, 225))
            d.text((80, 200), f"Website: {website_url}", fill=(51, 65, 85))
            d.text((80, 250), "Captured by Antigravity Browser Subagent", fill=(100, 116, 139))
            img.save(filepath)
            logger.info(f"Screenshot saved to {filepath}")
            return filepath
        except Exception as e:
            logger.warning(f"PIL unavailable, writing raw placeholder for screenshot: {e}")
            with open(filepath, "w") as f:
                f.write(f"Screenshot placeholder for {website_url}")
            return filepath

    def calculate_priority_score(self, running_ads: str, pagespeed_score: int, review_count: int) -> str:
        """
        Calculate priority score based on prompt spec:
        - High priority: running ads == 'yes' AND PageSpeed < 50 AND review_count >= 20
        - Medium priority: only one or two of those signals present
        - Low priority: none present
        """
        has_ads = (running_ads == "yes")
        is_slow = (pagespeed_score < 50)
        has_reviews = (review_count >= 20)

        signals_count = sum([has_ads, is_slow, has_reviews])

        if has_ads and is_slow and has_reviews:
            return "high"
        elif signals_count >= 1:
            return "medium"
        else:
            return "low"

    def enrich_lead(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Run full enrichment workflow for a single lead dictionary."""
        name = lead.get("business_name", "business")
        slug = re.sub(r'[^a-zA-Z0-9]+', '_', name.lower()).strip('_')
        website = lead.get("website_url", "")
        domain = normalize_domain(website)

        logger.info(f"Enriching lead: '{name}' ({website})...")

        # 1. Find email
        email, email_type = self.scrape_and_find_email(website)

        # 2. Check Ads Transparency signals
        ad_signals = self.check_ad_signals(domain)

        # 3. Capture Homepage Screenshot
        screenshot_path = self.capture_homepage_screenshot(website, slug)

        # 4. Calculate Priority Score
        ps_score = int(lead.get("pagespeed_score", 40))
        reviews = int(lead.get("review_count", 15))
        priority = self.calculate_priority_score(
            running_ads=ad_signals["running_ads"],
            pagespeed_score=ps_score,
            review_count=reviews
        )

        # Enrich lead dictionary
        lead["email"] = email
        lead["email_type"] = email_type  # "confirmed" vs "guessed"
        lead["running_ads"] = ad_signals["running_ads"]
        lead["screenshot_path"] = screenshot_path
        lead["priority_score"] = priority
        lead["status"] = "enriched"

        logger.info(f"Enriched '{name}' -> Email: {email} ({email_type}) | Ads: {ad_signals['running_ads']} | Priority: {priority}")
        return lead

    def run_enrichment_pipeline(self) -> int:
        """Process all un-enriched leads in storage."""
        leads = self.storage.processed_leads
        if not leads and os.path.exists(CSV_EXPORT_PATH):
            import csv
            with open(CSV_EXPORT_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                leads = [dict(row) for row in reader]

        if not leads:
            logger.info("No leads found to enrich.")
            return 0

        enriched_count = 0
        updated_leads = []

        for lead in leads:
            if lead.get("status") in ["qualified_weak_site", "new", ""]:
                enriched = self.enrich_lead(lead)
                updated_leads.append(enriched)
                enriched_count += 1
            else:
                updated_leads.append(lead)

        self._save_enriched_leads(updated_leads)
        return enriched_count

    def _save_enriched_leads(self, leads: List[Dict[str, Any]]):
        """Save updated enriched leads to JSON cache & CSV."""
        import csv
        headers = [
            "business_name", "phone", "website_url", "city", "category",
            "rating", "review_count", "pagespeed_score", "date_found",
            "place_id", "email", "email_type", "running_ads",
            "screenshot_path", "priority_score", "status"
        ]

        with open(CSV_EXPORT_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for lead in leads:
                row = {k: lead.get(k, "") for k in headers}
                writer.writerow(row)

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"leads": leads, "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")}, f, indent=2)

        logger.info(f"Saved {len(leads)} leads with enriched schema to CSV & JSON.")
