"""
Spec Site Generator Agent - Phase 2.5 Module.
Generates customized high-converting preview landing page sites for high and medium priority leads.
Uses trade-specific pre-written copy templates (HVAC, Plumbing, Roofing), stock photo libraries,
and dynamic injection of business name, city/service area, and phone number.
"""

import os
import re
import json
import logging
import urllib.parse
from typing import List, Dict, Any, Tuple, Optional

from lead_pipeline.config import DATA_DIR, CSV_EXPORT_PATH, CACHE_FILE
from lead_pipeline.sheets_exporter import LeadStorageEngine

logger = logging.getLogger("spec_site_generator")

PREVIEWS_DIR = os.path.join(DATA_DIR, "previews")
os.makedirs(PREVIEWS_DIR, exist_ok=True)

# Trade Category Copy Blocks & Theme Config
TRADE_TEMPLATES = {
    "hvac": {
        "tagline": "Fast, Reliable Heating & Air Conditioning Services",
        "hero_sub": "Keep your home comfortable year-round with certified local HVAC experts in {city}.",
        "services": [
            {"title": "24/7 Emergency AC Repairs", "desc": "Fast response times when your air conditioner breaks down in peak summer heat."},
            {"title": "Heating System Installations", "desc": "Energy-efficient heat pumps and furnace solutions tailored for {city} homes."},
            {"title": "Routine HVAC Maintenance", "desc": "Comprehensive filter replacements, safety checks, and performance optimization."}
        ],
        "primary_color": "#0284c7",
        "accent_color": "#38bdf8",
        "bg_dark": "#0f172a",
        "stock_photo": "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?auto=format&fit=crop&w=1200&q=80"
    },
    "plumbing": {
        "tagline": "Trusted Licensed Plumbers & Emergency Drainage",
        "hero_sub": "From burst pipes to modern bathroom renovations, top-rated plumbing in {city}.",
        "services": [
            {"title": "Blocked Drain Clearing", "desc": "Hydro-jetting and CCTV camera inspections to clear tough clogs quickly."},
            {"title": "Hot Water System Repairs", "desc": "Same-day hot water system replacements, gas, solar & electric units."},
            {"title": "24/7 Emergency Plumbing", "desc": "Immediate dispatch for leaks, burst pipes, and urgent water emergencies in {city}."}
        ],
        "primary_color": "#0d9488",
        "accent_color": "#2dd4bf",
        "bg_dark": "#042f2e",
        "stock_photo": "https://images.unsplash.com/photo-1585704032915-c3400ca199e7?auto=format&fit=crop&w=1200&q=80"
    },
    "roofing": {
        "tagline": "Premium Roofing Repairs, Restorations & Inspections",
        "hero_sub": "Protect your family home with durable, storm-resistant roofing in {city}.",
        "services": [
            {"title": "Full Roof Restorations", "desc": "High-pressure cleaning, repointing, tile replacement and heat-reflective coating."},
            {"title": "Leak Detection & Repair", "desc": "Rapid roof repair to prevent water damage during storm season."},
            {"title": "Guttering & Metal Roofing", "desc": "Colorbond installation, fascia repair, and leaf-guard protection system."}
        ],
        "primary_color": "#ea580c",
        "accent_color": "#f97316",
        "bg_dark": "#1c1917",
        "stock_photo": "https://images.unsplash.com/photo-1632759145351-1d592919f522?auto=format&fit=crop&w=1200&q=80"
    }
}

class SpecSiteGeneratorAgent:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    def _get_trade_key(self, category: str) -> str:
        cat_lower = category.lower()
        if "hvac" in cat_lower or "air" in cat_lower or "heat" in cat_lower:
            return "hvac"
        elif "plumb" in cat_lower or "drain" in cat_lower or "water" in cat_lower:
            return "plumbing"
        elif "roof" in cat_lower or "gutter" in cat_lower:
            return "roofing"
        return "hvac"  # Default fallback

    def validate_lead_data(self, lead: Dict[str, Any]) -> Tuple[bool, str]:
        """Check for data validity and design breaking conditions (e.g. name length overflow)."""
        name = lead.get("business_name", "").strip()
        phone = lead.get("phone", "").strip()
        city = lead.get("city", "").strip()

        if not name:
            return False, "Missing business name"
        if len(name) > 65:
            return False, "Business name too long (>65 chars), potential layout overflow"
        if not phone:
            return False, "Missing phone number for click-to-call button"
        if not city:
            return False, "Missing city/service location"

        return True, ""

    def generate_site_html(self, lead: Dict[str, Any]) -> str:
        """Generate static HTML landing page tailored to lead."""
        name = lead.get("business_name", "Trade Business")
        phone = lead.get("phone", "0000 000 000")
        city = lead.get("city", "Local Area")
        category = lead.get("category", "HVAC")

        trade_key = self._get_trade_key(category)
        tpl = TRADE_TEMPLATES[trade_key]

        tagline = tpl["tagline"]
        hero_sub = tpl["hero_sub"].format(city=city)
        services = tpl["services"]
        stock_photo = tpl["stock_photo"]

        services_html = ""
        for s in services:
            desc = s["desc"].format(city=city)
            services_html += f"""
            <div class="card">
                <h3>{s['title']}</h3>
                <p>{desc}</p>
            </div>
            """

        clean_phone = re.sub(r'[^0-9+]', '', phone)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Premier {category} Services in {city}</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: {tpl['primary_color']};
            --accent: {tpl['accent_color']};
            --bg-dark: {tpl['bg_dark']};
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Outfit', sans-serif; }}
        body {{ background-color: #f8fafc; color: #1e293b; line-height: 1.6; }}
        header {{ background: var(--bg-dark); color: #fff; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--primary); }}
        .logo {{ font-size: 22px; font-weight: 800; color: #fff; text-transform: uppercase; letter-spacing: 0.5px; }}
        .call-btn {{ background: var(--primary); color: #fff; padding: 12px 24px; font-weight: 700; border-radius: 8px; text-decoration: none; display: inline-flex; align-items: center; gap: 8px; transition: 0.2s; }}
        .call-btn:hover {{ background: var(--accent); color: #fff; }}
        
        .hero {{ background: linear-gradient(135deg, var(--bg-dark) 0%, #1e293b 100%); color: #fff; padding: 90px 40px; text-align: center; position: relative; overflow: hidden; }}
        .hero h1 {{ font-size: 48px; font-weight: 800; margin-bottom: 16px; max-width: 900px; margin-left: auto; margin-right: auto; line-height: 1.2; }}
        .hero p {{ font-size: 20px; color: #94a3b8; max-width: 700px; margin: 0 auto 30px auto; }}
        
        .preview-banner {{ background: #fef3c7; color: #92400e; padding: 12px; font-weight: 700; text-align: center; border-bottom: 1px solid #fde68a; font-size: 14px; }}

        .main-img {{ max-width: 1000px; margin: -50px auto 40px auto; display: block; width: 90%; height: 420px; object-fit: cover; border-radius: 16px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); border: 4px solid #fff; }}

        .container {{ max-width: 1100px; margin: 0 auto; padding: 40px 20px; }}
        .section-title {{ text-align: center; font-size: 32px; font-weight: 700; margin-bottom: 40px; }}
        .services-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; }}
        .card {{ background: #fff; padding: 32px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }}
        .card h3 {{ font-size: 22px; font-weight: 700; margin-bottom: 12px; color: var(--bg-dark); }}
        
        .cta-box {{ background: var(--bg-dark); color: #fff; padding: 60px 40px; border-radius: 16px; text-align: center; margin-top: 60px; }}
        .cta-box h2 {{ font-size: 36px; margin-bottom: 16px; }}
        .cta-box p {{ font-size: 18px; color: #94a3b8; margin-bottom: 30px; }}

        footer {{ background: #090d16; color: #64748b; padding: 30px; text-align: center; font-size: 14px; border-top: 1px solid #1e293b; }}
    </style>
</head>
<body>
    <div class="preview-banner">
        ⚡ DEMO PREVIEW GENERATED FOR {name.upper()} ({city.upper()})
    </div>

    <header>
        <div class="logo">🔧 {name}</div>
        <a href="tel:{clean_phone}" class="call-btn">📞 Call Now: {phone}</a>
    </header>

    <section class="hero">
        <h1>{tagline}</h1>
        <p>{hero_sub}</p>
        <a href="tel:{clean_phone}" class="call-btn" style="font-size: 18px; padding: 16px 36px;">Get Instant Quote — {phone}</a>
    </section>

    <img src="{stock_photo}" alt="{name} {category}" class="main-img">

    <div class="container">
        <h2 class="section-title">Our Expert Services in {city}</h2>
        <div class="services-grid">
            {services_html}
        </div>

        <div class="cta-box">
            <h2>Need a Qualified {category} Expert in {city}?</h2>
            <p>Fast dispatch, upfront pricing, and guaranteed quality craftsmanship.</p>
            <a href="tel:{clean_phone}" class="call-btn" style="font-size: 18px; padding: 16px 36px;">Call {name} Today</a>
        </div>
    </div>

    <footer>
        &copy; 2026 {name} • Serving {city} and surrounding areas. All rights reserved.
    </footer>
</body>
</html>"""
        return html

    def generate_spec_site(self, lead: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Generate site and deploy to unique slug directory."""
        valid, err_reason = self.validate_lead_data(lead)
        if not valid:
            lead["status"] = "generation_failed"
            lead["generation_error"] = err_reason
            logger.warning(f"Spec site generation failed for '{lead.get('business_name')}': {err_reason}")
            return False, err_reason, lead

        name = lead.get("business_name", "")
        slug = re.sub(r'[^a-zA-Z0-9]+', '_', name.lower()).strip('_')
        site_dir = os.path.join(PREVIEWS_DIR, slug)
        os.makedirs(site_dir, exist_ok=True)

        html = self.generate_site_html(lead)
        index_path = os.path.join(site_dir, "index.html")

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html)

        preview_url = f"{self.base_url}/previews/{slug}/index.html"
        lead["preview_url"] = preview_url
        lead["preview_path"] = index_path
        lead["status"] = "preview ready — pending QA"

        logger.info(f"Spec site generated successfully for '{name}' -> {preview_url}")
        return True, preview_url, lead

    def run_spec_site_pipeline(self) -> int:
        """Run Spec Site Generator on all High and Medium priority leads."""
        import csv
        leads = []
        if os.path.exists(CSV_EXPORT_PATH):
            with open(CSV_EXPORT_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                leads = [dict(row) for row in reader]

        if not leads:
            logger.info("No leads available for spec site generation.")
            return 0

        generated_count = 0
        updated_leads = []

        for lead in leads:
            priority = lead.get("priority_score", "low")
            status = lead.get("status", "")

            # Target high and medium priority leads that are enriched
            if priority in ["high", "medium"] and status in ["enriched", "qualified_weak_site"]:
                success, url_or_err, updated_lead = self.generate_spec_site(lead)
                updated_leads.append(updated_lead)
                if success:
                    generated_count += 1
            else:
                updated_leads.append(lead)

        self._save_spec_site_leads(updated_leads)
        return generated_count

    def _save_spec_site_leads(self, leads: List[Dict[str, Any]]):
        import csv
        headers = [
            "business_name", "phone", "website_url", "city", "category",
            "rating", "review_count", "pagespeed_score", "date_found",
            "place_id", "email", "email_type", "running_ads",
            "screenshot_path", "priority_score", "preview_url", "preview_path",
            "generation_error", "status"
        ]

        with open(CSV_EXPORT_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for lead in leads:
                row = {k: lead.get(k, "") for k in headers}
                writer.writerow(row)

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"leads": leads, "last_updated": os.getenv("CURRENT_TIME", "")}, f, indent=2)
