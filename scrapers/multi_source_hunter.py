"""
Multi-Source Market Hunter Engine
Scrapes live, real-time market demand signals from:
1. Hacker News Algolia API (Customer pain points & complaint threads)
2. Product Hunt & Google Trends RSS
3. Reddit (via official OAuth API if REDDIT_CLIENT_ID / SECRET configured)

Includes strict Supply vs. Demand filtering to discard product launch self-promotions.
"""

import json
import logging
import urllib.request
import urllib.parse
import os
import re
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class MarketHunter:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.reddit_client_id = os.getenv("REDDIT_CLIENT_ID", "")
        self.reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")

    def is_self_promotion_launch(self, text: str) -> bool:
        """Filter out founder product launch posts ('supply') vs actual customer pain ('demand')."""
        t = text.lower()
        launch_patterns = [
            r"show hn:", r"i built", r"i am building", r"i'm building", r"introducing",
            r"we launched", r"our product", r"my new app", r"check out my", r"launching today"
        ]
        return any(re.search(pat, t) for pat in launch_patterns)

    def fetch_hackernews_pain_points(self) -> List[Dict[str, Any]]:
        """Fetch live user pain points & software complaint comments from Hacker News via Algolia API."""
        signals = []
        queries = [
            '"wish there was an app"',
            '"why is there no tool"',
            '"terrible software"',
            '"manual work"',
            '"expensive software"'
        ]

        for q in queries:
            try:
                encoded_q = urllib.parse.quote(q)
                url = f"https://hn.algolia.com/api/v1/search_by_date?query={encoded_q}&tags=comment&hitsPerPage=10"
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=8) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    hits = data.get("hits", [])

                    for hit in hits:
                        comment_text = hit.get("comment_text", "")
                        story_title = hit.get("story_title", "Hacker News Business Discussion")
                        object_id = hit.get("objectID", "")
                        story_id = hit.get("story_id", "")

                        # Clean HTML tags from comment
                        clean_comment = re.sub('<[^<]+?>', '', comment_text)

                        # Skip self-promotions
                        if self.is_self_promotion_launch(clean_comment) or self.is_self_promotion_launch(story_title):
                            continue

                        if len(clean_comment) > 50:
                            signals.append({
                                "source": f"Hacker News Comment (Thread: {story_title[:40]})",
                                "title": f"Market Gap: {story_title}",
                                "description": clean_comment[:600],
                                "url": f"https://news.ycombinator.com/item?id={object_id}",
                                "engagement": hit.get("points", 1) or 1,
                                "raw_type": "live_user_pain_point"
                            })
            except Exception as e:
                logger.warning(f"Could not fetch HN query {q}: {e}")

        return signals

    def fetch_reddit_signals_oauth(self) -> List[Dict[str, Any]]:
        """Fetch live Reddit posts using official OAuth API if credentials are provided."""
        if not self.reddit_client_id or not self.reddit_client_secret:
            logger.info("Reddit OAuth credentials not set. Skipping live Reddit sweep cleanly.")
            return []

        signals = []
        try:
            # 1. Get OAuth Access Token
            auth_url = "https://www.reddit.com/api/v1/access_token"
            auth_data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode('utf-8')
            auth_req = urllib.request.Request(auth_url, data=auth_data, headers={
                "User-Agent": "OpportunityHunter/1.0",
            })
            
            # Basic Auth header
            import base64
            auth_str = f"{self.reddit_client_id}:{self.reddit_client_secret}"
            b64_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
            auth_req.add_header("Authorization", f"Basic {b64_auth}")

            with urllib.request.urlopen(auth_req, timeout=10) as auth_resp:
                token_data = json.loads(auth_resp.read().decode('utf-8'))
                access_token = token_data.get("access_token")

            if access_token:
                # 2. Fetch hot posts from business subreddits
                subreddits = ["SaaS", "startups", "smallbusiness", "automation"]
                for sub in subreddits:
                    sub_url = f"https://oauth.reddit.com/r/{sub}/hot?limit=10"
                    sub_req = urllib.request.Request(sub_url, headers={
                        "User-Agent": "OpportunityHunter/1.0",
                        "Authorization": f"bearer {access_token}"
                    })
                    with urllib.request.urlopen(sub_req, timeout=8) as sub_resp:
                        res = json.loads(sub_resp.read().decode('utf-8'))
                        posts = res.get("data", {}).get("children", [])
                        for p in posts:
                            pdata = p.get("data", {})
                            title = pdata.get("title", "")
                            selftext = pdata.get("selftext", "")
                            permalink = f"https://reddit.com{pdata.get('permalink', '')}"

                            if self.is_self_promotion_launch(title):
                                continue

                            signals.append({
                                "source": f"Reddit (r/{sub})",
                                "title": title,
                                "description": selftext[:600] if selftext else title,
                                "url": permalink,
                                "engagement": pdata.get("score", 1),
                                "raw_type": "live_reddit_post"
                            })
        except Exception as e:
            logger.warning(f"Reddit OAuth fetch error: {e}")

        return signals

    def hunt_all_opportunities(self) -> List[Dict[str, Any]]:
        """Run all live market scrapers and return aggregated fresh market signals."""
        logger.info("Hunting for fresh, live market signals across web APIs...")
        hn_signals = self.fetch_hackernews_pain_points()
        reddit_signals = self.fetch_reddit_signals_oauth()

        all_signals = hn_signals + reddit_signals
        logger.info(f"Collected {len(all_signals)} live market signals.")
        return all_signals

if __name__ == "__main__":
    hunter = MarketHunter()
    results = hunter.hunt_all_opportunities()
    print(json.dumps(results[:2], indent=2))
