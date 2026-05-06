"""
Bluesky Scraper - Uses the AT Protocol public API (completely free).
Bluesky is a Twitter alternative with an open API.
"""

import requests
from datetime import datetime


class BlueskyScraper:
    """Scrapes Bluesky (AT Protocol) for public posts about a location"""

    def __init__(self):
        # Bluesky public search API
        self.search_url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"

    def scrape(self, location, timeout=15):
        """
        Search Bluesky for posts about the given location.
        Returns list of {text, source, timestamp, location}
        """
        results = []

        # Search queries
        queries = [
            f"{location} crisis",
            f"{location} emergency disaster",
            f"{location} flood earthquake fire",
            f"{location}",
        ]

        for query in queries:
            try:
                params = {
                    "q": query,
                    "limit": 20,
                    "sort": "latest",
                }

                response = requests.get(
                    self.search_url, params=params, timeout=timeout
                )

                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("posts", [])

                    for post in posts:
                        record = post.get("record", {})
                        text = record.get("text", "")
                        created_at = record.get("createdAt", "")

                        if len(text) > 10:
                            # Parse timestamp
                            try:
                                ts = datetime.fromisoformat(
                                    created_at.replace("Z", "+00:00")
                                )
                            except Exception:
                                ts = datetime.now()

                            # Get author info
                            author = post.get("author", {})
                            handle = author.get("handle", "unknown")

                            results.append({
                                "text": text[:500],
                                "source": "bluesky",
                                "timestamp": ts.isoformat(),
                                "location": location,
                                "url": f"https://bsky.app/profile/{handle}",
                                "author": handle,
                            })

            except Exception as e:
                print(f"Bluesky scraper error: {e}")
                continue

        return results
