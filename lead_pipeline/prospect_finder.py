"""
Prospect Finder Agent - Phase 1 Lead Generation Module for Local Trade Businesses.
Queries Google Places API & PageSpeed Insights API, applies quality filters, deduplicates, and saves output.
"""

import os
import json
import time
import logging
import urllib.parse
import urllib.request
from datetime import datetime
from typing import List, Dict, Any, Optional

from lead_pipeline.config import (
    GOOGLE_PLACES_API_KEY,
    GOOGLE_PAGESPEED_API_KEY,
    DEFAULT_TARGET_CITIES,
    DEFAULT_TRADE_CATEGORIES,
    MIN_REVIEW_COUNT,
    MAX_PAGESPEED_SCORE,
    DEFAULT_COUNTRY_CODE,
    LOG_FILE
)
from lead_pipeline.sheets_exporter import LeadStorageEngine

logger = logging.getLogger("prospect_finder")

class ProspectFinderAgent:
    def __init__(self, places_api_key: str = "", pagespeed_api_key: str = ""):
        self.places_key = places_api_key or GOOGLE_PLACES_API_KEY
        self.pagespeed_key = pagespeed_api_key or GOOGLE_PAGESPEED_API_KEY
        self.storage = LeadStorageEngine()

    def search_google_places(self, category: str, city: str) -> List[Dict[str, Any]]:
        """Query Google Places Text Search API for a specific category + city combo in Australia."""
        if not self.places_key:
            logger.warning(f"No Google Places API key found. Generating sample data for '{category}' in '{city}'.")
            return self._generate_sample_places(category, city)

        query = f"{category} in {city}, Australia"
        url = (
            f"https://maps.googleapis.com/maps/api/place/textsearch/json?"
            f"query={urllib.parse.quote(query)}&region={DEFAULT_COUNTRY_CODE.lower()}&key={self.places_key}"
        )

        results = []
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AntigravityProspectFinder/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                status = data.get("status")
                if status == "OK":
                    results = data.get("results", [])
                    logger.info(f"Google Places returned {len(results)} places for query '{query}'.")
                else:
                    logger.error(f"Google Places API error status '{status}' for query '{query}': {data.get('error_message')}")
        except Exception as e:
            logger.error(f"HTTP exception during Google Places search for '{query}': {e}")

        # Enhance each place result with place details (website & phone if missing in textsearch)
        enhanced_results = []
        for place in results:
            place_id = place.get("place_id")
            detail = self.get_place_details(place_id) if place_id else {}
            
            website = detail.get("website") or place.get("website", "")
            phone = detail.get("formatted_phone_number") or place.get("formatted_phone_number", "")
            
            enhanced_results.append({
                "place_id": place_id,
                "business_name": place.get("name", ""),
                "formatted_address": place.get("formatted_address", ""),
                "phone": phone,
                "website_url": website,
                "rating": place.get("rating", 0.0),
                "review_count": place.get("user_ratings_total", 0),
                "city": city,
                "category": category
            })
            time.sleep(0.1)  # Rate limit courtesy

        return enhanced_results

    def _generate_sample_places(self, category: str, city: str) -> List[Dict[str, Any]]:
        """Generate realistic sample Australian prospects for dry-run testing when API key is missing."""
        city_clean = city.split(",")[0].lower().replace(" ", "")
        cat_clean = category.lower().replace(" ", "")
        tag = int(time.time()) % 10000
        
        return [
            {
                "place_id": f"place_au_{city_clean}_{cat_clean}_01_{tag}",
                "business_name": f"{city.split(',')[0]} Premium {category} Services #{tag}",
                "formatted_address": f"100 Commercial Rd, {city}, Australia",
                "phone": f"02 9123 {tag:04d}",
                "website_url": f"http://www.{city_clean}{cat_clean}services{tag}.com.au",
                "rating": 4.6,
                "review_count": 34,  # Qualified: >= 10
                "city": city,
                "category": category,
                "_mock_pagespeed": 32  # Qualified: < 50
            },
            {
                "place_id": f"place_au_{city_clean}_{cat_clean}_02_{tag}",
                "business_name": f"A1 {category} Solutions {city.split(',')[0]} #{tag}",
                "formatted_address": f"45 Industrial Pkwy, {city}, Australia",
                "phone": f"02 9888 {tag:04d}",
                "website_url": f"http://www.a1{cat_clean}{city_clean}{tag}.com.au",
                "rating": 4.8,
                "review_count": 52,  # Qualified: >= 10
                "city": city,
                "category": category,
                "_mock_pagespeed": 41  # Qualified: < 50
            },
            {
                "place_id": f"place_au_{city_clean}_{cat_clean}_03_{tag}",
                "business_name": f"Newbie {category} Co #{tag}",
                "formatted_address": f"12 Suburban St, {city}, Australia",
                "phone": f"04 1234 {tag:04d}",
                "website_url": f"http://www.newbie{cat_clean}{tag}.com.au",
                "rating": 5.0,
                "review_count": 3,   # Unqualified: < 10 reviews
                "city": city,
                "category": category,
                "_mock_pagespeed": 20
            },
            {
                "place_id": f"place_au_{city_clean}_{cat_clean}_04_{tag}",
                "business_name": f"Fast Modern {category} Hub #{tag}",
                "formatted_address": f"88 High St, {city}, Australia",
                "phone": f"02 9333 {tag:04d}",
                "website_url": f"http://www.fast{cat_clean}{tag}.com.au",
                "rating": 4.7,
                "review_count": 68,
                "city": city,
                "category": category,
                "_mock_pagespeed": 88  # Unqualified: >= 50 PageSpeed
            }
        ]

    def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """Fetch detailed contact info (website, phone) for a place_id."""
        if not self.places_key or not place_id:
            return {}

        url = (
            f"https://maps.googleapis.com/maps/api/place/details/json?"
            f"place_id={place_id}&fields=name,website,formatted_phone_number&key={self.places_key}"
        )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AntigravityProspectFinder/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("status") == "OK":
                    return data.get("result", {})
        except Exception as e:
            logger.error(f"Failed to fetch place details for {place_id}: {e}")
        return {}

    def fetch_pagespeed_score(self, website_url: str, fallback_mock: Optional[int] = None) -> Optional[int]:
        """Query Google PageSpeed Insights API for mobile Lighthouse performance score (0-100)."""
        if not website_url:
            return None

        if not self.pagespeed_key:
            if fallback_mock is not None:
                return fallback_mock
            return 35  # Default mock weak score if no key provided

        key_param = f"&key={self.pagespeed_key}" if self.pagespeed_key else ""
        url = (
            f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?"
            f"url={urllib.parse.quote(website_url)}&strategy=mobile{key_param}"
        )

        try:
            logger.info(f"Checking PageSpeed score for {website_url}...")
            req = urllib.request.Request(url, headers={"User-Agent": "AntigravityProspectFinder/1.0"})
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                score = (
                    data.get("lighthouseResult", {})
                    .get("categories", {})
                    .get("performance", {})
                    .get("score")
                )
                if score is not None:
                    return int(round(score * 100))
        except Exception as e:
            logger.error(f"PageSpeed API call failed for {website_url}: {e}")
            if fallback_mock is not None:
                return fallback_mock
        return None

    def filter_and_qualify_prospects(self, raw_prospects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply Phase 1 filters: review count >= 10, website present, mobile PageSpeed < 50."""
        qualified = []
        for p in raw_prospects:
            name = p.get("business_name")
            reviews = p.get("review_count", 0)
            website = p.get("website_url")

            # Check 1: Review count filter (>= 10)
            if reviews < MIN_REVIEW_COUNT:
                logger.info(f"Filtered out '{name}': review count ({reviews}) < {MIN_REVIEW_COUNT}.")
                continue

            # Check 2: Website presence filter
            if not website:
                logger.info(f"Filtered out '{name}': no website URL listed.")
                continue

            # Check 3: Check deduplication engine before performing expensive PageSpeed check
            if self.storage.is_duplicate(p):
                logger.info(f"Filtered out '{name}': already processed in lead database.")
                continue

            # Check 4: PageSpeed score filter (< 50)
            ps_score = self.fetch_pagespeed_score(website, fallback_mock=p.get("_mock_pagespeed"))
            if ps_score is None:
                logger.warning(f"Could not calculate PageSpeed score for '{name}' ({website}). Skipping.")
                continue

            if ps_score >= MAX_PAGESPEED_SCORE:
                logger.info(f"Filtered out '{name}': PageSpeed score ({ps_score}) >= {MAX_PAGESPEED_SCORE} (site is too fast/healthy).")
                continue

            # Qualified weak-website prospect target found!
            lead = {
                "business_name": name,
                "phone": p.get("phone", ""),
                "website_url": website,
                "city": p.get("city", ""),
                "category": p.get("category", ""),
                "rating": p.get("rating", 0.0),
                "review_count": reviews,
                "pagespeed_score": ps_score,
                "date_found": datetime.now().strftime("%Y-%m-%d"),
                "place_id": p.get("place_id", ""),
                "status": "qualified_weak_site"
            }
            logger.info(f"🎯 QUALIFIED PROSPECT: '{name}' | City: {p.get('city')} | PageSpeed: {ps_score} | Reviews: {reviews}")
            qualified.append(lead)

        return qualified

    def run_pipeline(self, cities: List[str] = None, categories: List[str] = None) -> int:
        """Run Phase 1 prospect finder across all specified cities and trade categories."""
        target_cities = cities or DEFAULT_TARGET_CITIES
        target_categories = categories or DEFAULT_TRADE_CATEGORIES

        logger.info(f"Starting Phase 1 Prospect Finder run for {len(target_cities)} cities & {len(target_categories)} categories.")
        all_qualified = []

        for city in target_cities:
            for cat in target_categories:
                logger.info(f"🔎 Querying: Category='{cat}' in City='{city}'...")
                raw_leads = self.search_google_places(cat, city)
                qualified = self.filter_and_qualify_prospects(raw_leads)
                all_qualified.extend(qualified)

        saved_count = self.storage.save_leads(all_qualified)
        logger.info(f"Finished Phase 1 run. Total new qualified prospects added: {saved_count}")
        return saved_count
