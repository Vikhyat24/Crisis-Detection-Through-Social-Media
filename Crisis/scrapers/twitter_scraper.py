"""
Twitter/X Scraper - Uses Selenium to scrape public tweets.
Supports geocode-based search when lat/lon/radius are provided.
NOTE: Twitter actively blocks bots. This may not always work.
      You need Chrome browser + ChromeDriver installed.
"""

import time
from datetime import datetime

# Selenium imports - may not be installed
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False


class TwitterScraper:
    """Scrapes Twitter/X using Selenium web browser automation"""

    def __init__(self):
        self.driver = None

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
            print(f"Could not create Chrome driver: {e}")
            return None

    def scrape(self, location, lat=None, lon=None, radius_km=50, timeout=20):
        """
        Search Twitter/X for tweets about the given location.
        If lat/lon provided, uses geocode search parameter.
        Returns list of {text, source, timestamp, location, url}
        """
        results = []

        if not HAS_SELENIUM:
            print("Selenium not installed. Skipping Twitter scraper.")
            return results

        driver = self._create_driver()
        if not driver:
            print("Could not start Chrome. Skipping Twitter scraper.")
            return results

        try:
            # Build search query with geocode if coordinates available
            crisis_terms = "crisis OR emergency OR disaster OR flood OR earthquake OR fire"
            search_query = f"{location} {crisis_terms}"

            # Add geocode parameter if we have coordinates
            if lat is not None and lon is not None:
                geocode_param = f" geocode:{lat},{lon},{radius_km}km"
                search_query += geocode_param

            encoded_query = search_query.replace(" ", "%20")

            # Try Twitter search
            search_url = f"https://x.com/search?q={encoded_query}&src=typed_query&f=live"

            driver.get(search_url)
            time.sleep(5)

            # Try to find tweet elements
            try:
                tweets = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, '[data-testid="tweetText"]')
                    )
                )

                for tweet in tweets[:30]:
                    text = tweet.text.strip()
                    if len(text) > 10:
                        results.append({
                            "text": text[:500],
                            "source": "twitter",
                            "timestamp": datetime.now().isoformat(),
                            "location": location,
                            "url": search_url,
                        })
            except Exception:
                print("Twitter may require login or blocked the request.")
                # Fallback: try Nitter
                nitter_results = self._try_nitter(driver, location)
                results.extend(nitter_results)

        except Exception as e:
            print(f"Twitter scraper error: {e}")
        finally:
            try:
                driver.quit()
            except Exception:
                pass

        return results

    def _try_nitter(self, driver, location):
        """Try Nitter instances as Twitter fallback"""
        results = []
        nitter_instances = [
            "https://nitter.net",
            "https://nitter.privacydev.net",
        ]

        search_query = f"{location} crisis emergency disaster"

        for nitter_url in nitter_instances:
            try:
                encoded = search_query.replace(" ", "+")
                url = f"{nitter_url}/search?f=tweets&q={encoded}"
                driver.get(url)
                time.sleep(3)

                tweets = driver.find_elements(By.CSS_SELECTOR, ".tweet-content")

                for tweet in tweets[:20]:
                    text = tweet.text.strip()
                    if len(text) > 10:
                        results.append({
                            "text": text[:500],
                            "source": "twitter_nitter",
                            "timestamp": datetime.now().isoformat(),
                            "location": location,
                            "url": url,
                        })

                if results:
                    break

            except Exception as e:
                print(f"Nitter instance {nitter_url} failed: {e}")
                continue

        return results
