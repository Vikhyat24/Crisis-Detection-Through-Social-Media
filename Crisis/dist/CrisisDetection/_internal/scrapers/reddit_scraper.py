"""
Reddit Scraper - Uses Reddit's public JSON API (no auth needed)
Searches for crisis-related posts mentioning a location.
Supports geographic filtering via place name + radius.
"""

import requests
import time
from datetime import datetime


class RedditScraper:
    """Scrapes Reddit for crisis-related posts about a location"""

    def __init__(self):
        self.base_url = "https://www.reddit.com"
        self.headers = {
            "User-Agent": "CrisisDetectionBot/1.0 (Educational Research Project)"
        }

    def scrape(self, location, lat=None, lon=None, radius_km=50, timeout=15):
        """
        Search Reddit for posts about the given location.
        lat/lon/radius_km are used for context but Reddit search is text-based.
        Returns list of {text, source, timestamp, location, url}
        """
        results = []

        # Build location-aware subreddits to search
        location_subreddits = self._get_location_subreddits(location)

        # Search queries combining location with crisis keywords
        queries = [
            f"{location} crisis",
            f"{location} emergency",
            f"{location} disaster",
            f"{location} flood earthquake fire",
            f"{location}",
        ]

        # Search in general Reddit
        for query in queries:
            try:
                url = f"{self.base_url}/search.json"
                params = {
                    "q": query,
                    "sort": "new",
                    "limit": 25,
                    "t": "day",  # last 24 hours
                }
                response = requests.get(
                    url, params=params, headers=self.headers, timeout=timeout
                )

                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("data", {}).get("children", [])
                    self._extract_posts(posts, location, results)

                elif response.status_code == 429:
                    print("Reddit rate limited, backing off...")
                    time.sleep(3)
                    break

                # Rate limit: don't hammer Reddit
                time.sleep(1)

            except Exception as e:
                print(f"Reddit scraper error for query '{query}': {e}")
                continue

        # Also search location-specific subreddits
        for subreddit in location_subreddits[:3]:
            try:
                url = f"{self.base_url}/r/{subreddit}/new.json"
                params = {"limit": 15, "t": "day"}
                response = requests.get(
                    url, params=params, headers=self.headers, timeout=timeout
                )

                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("data", {}).get("children", [])
                    self._extract_posts(posts, location, results)

                time.sleep(1)

            except Exception as e:
                print(f"Reddit subreddit scraper error for r/{subreddit}: {e}")
                continue

        return results

    def _extract_posts(self, posts, location, results):
        """Extract post data from Reddit API response"""
        for post in posts:
            post_data = post.get("data", {})
            title = post_data.get("title", "")
            body = post_data.get("selftext", "")
            text = f"{title}. {body}".strip()

            if len(text) > 10:
                results.append({
                    "text": text[:500],
                    "source": "reddit",
                    "timestamp": datetime.fromtimestamp(
                        post_data.get("created_utc", time.time())
                    ).isoformat(),
                    "location": location,
                    "url": f"https://reddit.com{post_data.get('permalink', '')}",
                })

    def _get_location_subreddits(self, location):
        """Map location names to relevant subreddits"""
        location_lower = location.lower()

        subreddit_map = {
            "india": ["india", "IndiaSpeaks", "indianews"],
            "mumbai": ["mumbai", "india"],
            "delhi": ["delhi", "india"],
            "chennai": ["chennai", "india"],
            "bangalore": ["bangalore", "india"],
            "bengaluru": ["bangalore", "india"],
            "hyderabad": ["hyderabad", "india"],
            "kolkata": ["kolkata", "india"],
            "pune": ["pune", "india"],
            "tamil nadu": ["chennai", "india"],
            "maharashtra": ["mumbai", "india"],
            "kerala": ["Kerala", "india"],
            "karnataka": ["bangalore", "india"],
            "usa": ["news", "usa"],
            "new york": ["nyc", "news"],
            "california": ["California", "news"],
            "london": ["london", "unitedkingdom"],
            "japan": ["japan", "japannews"],
            "tokyo": ["tokyo", "japan"],
        }

        for key, subs in subreddit_map.items():
            if key in location_lower:
                return subs

        return ["worldnews", "news"]
