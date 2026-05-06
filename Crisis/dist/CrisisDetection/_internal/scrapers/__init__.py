"""
Multi-Source Scraper Module
Scrapes data from Reddit, Twitter, Instagram, Threads, GDELT, News RSS, and Bluesky.
All scrapers run in parallel and return unified format.
Supports location + radius based searching.
"""

import threading
import time
from scrapers.reddit_scraper import RedditScraper
from scrapers.gdelt_scraper import GDELTScraper
from scrapers.news_scraper import NewsScraper
from scrapers.bluesky_scraper import BlueskyScraper
from scrapers.twitter_scraper import TwitterScraper
from scrapers.instagram_scraper import InstagramScraper
from scrapers.threads_scraper import ThreadsScraper


class MultiSourceScraper:
    """Runs all scrapers in parallel and combines results"""

    def __init__(self):
        self.scrapers = {
            "reddit": RedditScraper(),
            "gdelt": GDELTScraper(),
            "news": NewsScraper(),
            "bluesky": BlueskyScraper(),
            "twitter": TwitterScraper(),
            "instagram": InstagramScraper(),
            "threads": ThreadsScraper(),
        }
        self.last_results = []
        self.is_running = False

    def scrape(self, location, lat=None, lon=None, radius_km=50, timeout=30):
        """
        Scrape all sources for a given location.
        Passes lat/lon/radius to scrapers that support geo filtering.
        Returns (list of dicts, errors dict)
        """
        self.is_running = True
        all_results = []
        errors = {}

        # Run each scraper in its own thread
        threads = []
        results_lock = threading.Lock()

        def run_scraper(name, scraper):
            try:
                # Pass geo params to scrapers that accept them
                try:
                    data = scraper.scrape(
                        location, lat=lat, lon=lon,
                        radius_km=radius_km, timeout=timeout
                    )
                except TypeError:
                    # Fallback for scrapers that don't accept geo params
                    data = scraper.scrape(location, timeout=timeout)

                with results_lock:
                    all_results.extend(data)
            except Exception as e:
                with results_lock:
                    errors[name] = str(e)

        for name, scraper in self.scrapers.items():
            t = threading.Thread(target=run_scraper, args=(name, scraper))
            t.daemon = True
            threads.append(t)
            t.start()

        # Wait for all threads to finish (with timeout)
        for t in threads:
            t.join(timeout=timeout)

        self.is_running = False

        # Remove duplicates based on text similarity
        seen_texts = set()
        unique_results = []
        for item in all_results:
            # Use first 100 chars as key for dedup
            key = item.get("text", "")[:100].lower().strip()
            if key and key not in seen_texts:
                seen_texts.add(key)
                unique_results.append(item)

        self.last_results = unique_results
        return unique_results, errors

    def get_active_sources(self):
        """Return list of scraper names"""
        return list(self.scrapers.keys())
