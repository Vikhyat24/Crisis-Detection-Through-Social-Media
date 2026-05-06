"""
GDELT Scraper - Uses GDELT DOC API (completely free, no key needed)
GDELT monitors news and events from around the world in real-time.
"""

import requests
from datetime import datetime


class GDELTScraper:
    """Scrapes GDELT for real-time global event data about a location"""

    def __init__(self):
        # GDELT DOC 2.0 API - try both URL formats
        self.base_urls = [
            "https://api.gdeltproject.org/api/v2/doc/doc",
            "https://api.gdeltproject.org/api/v2/doc/doc?query={query}&mode=artlist&maxrecords=30&format=json&sort=datedesc&timespan=24h",
        ]

    def scrape(self, location, timeout=15):
        """
        Search GDELT for news/events about the given location.
        Returns list of {text, source, timestamp, location}
        """
        results = []

        # Search for crisis-related content at this location
        queries = [
            f"{location} crisis OR disaster OR emergency OR flood OR earthquake",
            f"{location} fire OR storm OR cyclone OR accident OR attack",
        ]

        for query in queries:
            try:
                params = {
                    "query": query,
                    "mode": "artlist",
                    "maxrecords": 30,
                    "format": "json",
                    "sort": "datedesc",
                    "timespan": "24h",
                }

                response = requests.get(
                    self.base_urls[0], params=params, timeout=timeout
                )

                if response.status_code == 200:
                    # Check if response is valid JSON
                    text = response.text.strip()
                    if not text or text[0] not in ('{', '['):
                        print(f"GDELT returned non-JSON response, skipping.")
                        continue
                    
                    data = response.json()
                    articles = data.get("articles", [])

                    for article in articles:
                        title = article.get("title", "")
                        # GDELT gives us the article title and URL
                        if len(title) > 10:
                            # Parse GDELT date format (YYYYMMDDHHMMSS)
                            date_str = article.get("seendate", "")
                            try:
                                ts = datetime.strptime(date_str, "%Y%m%dT%H%M%SZ")
                            except Exception:
                                ts = datetime.now()

                            results.append({
                                "text": title[:500],
                                "source": "gdelt",
                                "timestamp": ts.isoformat(),
                                "location": location,
                                "url": article.get("url", ""),
                            })

            except Exception as e:
                print(f"GDELT scraper error: {e}")
                continue

        return results
