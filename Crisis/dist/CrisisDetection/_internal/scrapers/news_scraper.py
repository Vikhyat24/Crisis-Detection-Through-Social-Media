"""
News RSS Scraper - Parses Google News RSS feed for location-based news.
No API key needed. Uses feedparser to read RSS feeds.
"""

import requests
from datetime import datetime
import re

# Try to import feedparser, fall back to manual XML parsing
try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False


class NewsScraper:
    """Scrapes Google News and other RSS feeds for a location"""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def scrape(self, location, timeout=15):
        """
        Fetch news articles about the given location from RSS feeds.
        Returns list of {text, source, timestamp, location}
        """
        results = []

        # Google News RSS search
        google_news_results = self._scrape_google_news(location, timeout)
        results.extend(google_news_results)

        return results

    def _scrape_google_news(self, location, timeout):
        """Scrape Google News RSS for location-based news"""
        results = []

        # Search terms
        searches = [
            f"{location} crisis disaster emergency",
            f"{location} flood earthquake fire storm",
            f"{location}",
        ]

        for search_term in searches:
            try:
                # Google News RSS URL
                encoded_query = requests.utils.quote(search_term)
                url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"

                if HAS_FEEDPARSER:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:15]:
                        title = entry.get("title", "")
                        summary = entry.get("summary", "")
                        # Strip HTML tags from summary
                        summary = re.sub(r'<[^>]+>', '', summary).strip()
                        text = f"{title}. {summary}".strip()

                        # Parse date
                        try:
                            ts = datetime(*entry.published_parsed[:6])
                        except Exception:
                            ts = datetime.now()

                        if len(title) > 10:
                            results.append({
                                "text": text[:500],
                                "source": "google_news",
                                "timestamp": ts.isoformat(),
                                "location": location,
                                "url": entry.get("link", ""),
                            })
                else:
                    # Fallback: raw XML parsing if feedparser not installed
                    response = requests.get(url, headers=self.headers, timeout=timeout)
                    if response.status_code == 200:
                        # Simple regex extraction from RSS XML
                        titles = re.findall(r"<title>(.*?)</title>", response.text)
                        links = re.findall(r"<link>(.*?)</link>", response.text)

                        for i, title in enumerate(titles[2:17], start=2):  # skip feed title
                            if len(title) > 10:
                                link = links[i] if i < len(links) else ""
                                results.append({
                                    "text": title[:500],
                                    "source": "google_news",
                                    "timestamp": datetime.now().isoformat(),
                                    "location": location,
                                    "url": link,
                                })

            except Exception as e:
                print(f"News scraper error: {e}")
                continue

        return results
