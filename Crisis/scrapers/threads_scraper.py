"""
Threads Scraper - Uses Selenium to scrape Meta's Threads platform.
Searches for location + crisis keywords on threads.net.

NOTE: Threads may require login or block automated access.
      This is best-effort and may return 0 results.
"""

import time
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False


class ThreadsScraper:
    """Scrapes Meta Threads for crisis-related posts about a location"""

    def __init__(self):
        self.base_url = "https://www.threads.net"

    def _create_driver(self):
        """Create a headless Chrome browser"""
        if not HAS_SELENIUM:
            return None

        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            chrome_options.add_argument("--blink-settings=imagesEnabled=false")

            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(20)
            return driver
        except Exception as e:
            print(f"Threads: Could not create Chrome driver: {e}")
            return None

    def scrape(self, location, lat=None, lon=None, radius_km=50, timeout=20):
        """
        Search Threads for posts about the given location.
        Returns list of {text, source, timestamp, location, url}
        """
        results = []

        if not HAS_SELENIUM:
            print("Selenium not installed. Skipping Threads scraper.")
            return results

        driver = self._create_driver()
        if not driver:
            print("Could not start Chrome. Skipping Threads scraper.")
            return results

        try:
            # Search queries
            queries = [
                f"{location} crisis",
                f"{location} emergency disaster",
                f"{location} flood earthquake",
                location,
            ]

            for query in queries[:3]:
                try:
                    encoded = query.replace(" ", "%20")
                    url = f"{self.base_url}/search?q={encoded}&serp_type=default"
                    driver.get(url)
                    time.sleep(4)

                    # Try multiple CSS selectors for thread posts
                    post_selectors = [
                        '[data-pressable-container="true"]',
                        'div[class*="BodyTextContainer"]',
                        'span[dir="auto"]',
                        'div[role="article"]',
                    ]

                    for selector in post_selectors:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            for el in elements[:15]:
                                text = el.text.strip()
                                if len(text) > 15 and len(text) < 1000:
                                    results.append({
                                        "text": text[:500],
                                        "source": "threads",
                                        "timestamp": datetime.now().isoformat(),
                                        "location": location,
                                        "url": url,
                                    })
                            if results:
                                break

                    time.sleep(2)

                except Exception as e:
                    print(f"Threads search error for '{query}': {e}")
                    continue

        except Exception as e:
            print(f"Threads scraper error: {e}")
        finally:
            try:
                driver.quit()
            except Exception:
                pass

        return results
