"""
Instagram Scraper - Uses Selenium to scrape public Instagram posts.
Searches by hashtag (e.g., #Mumbai, #MumbaiFlood) since Instagram
has no free text search API.

NOTE: Instagram actively blocks automated access. This is best-effort
      and may return 0 results if blocked.
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


class InstagramScraper:
    """Scrapes Instagram for crisis-related posts about a location"""

    def __init__(self):
        self.base_url = "https://www.instagram.com"

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
            print(f"Instagram: Could not create Chrome driver: {e}")
            return None

    def scrape(self, location, lat=None, lon=None, radius_km=50, timeout=20):
        """
        Search Instagram for posts about the given location via hashtags.
        Returns list of {text, source, timestamp, location, url}
        """
        results = []

        if not HAS_SELENIUM:
            print("Selenium not installed. Skipping Instagram scraper.")
            return results

        driver = self._create_driver()
        if not driver:
            print("Could not start Chrome. Skipping Instagram scraper.")
            return results

        try:
            # Build hashtags from location name
            location_clean = location.replace(" ", "").lower()
            hashtags = [
                location_clean,
                f"{location_clean}flood",
                f"{location_clean}earthquake",
                f"{location_clean}crisis",
                f"{location_clean}emergency",
            ]

            for tag in hashtags[:3]:  # Limit to avoid rate limiting
                try:
                    url = f"{self.base_url}/explore/tags/{tag}/"
                    driver.get(url)
                    time.sleep(4)

                    # Try to find post links and get their alt text/captions
                    # Instagram uses <article> elements with images that have alt text
                    articles = driver.find_elements(By.CSS_SELECTOR, "article img[alt]")

                    for img in articles[:10]:
                        alt_text = img.get_attribute("alt") or ""
                        if len(alt_text) > 15:
                            results.append({
                                "text": alt_text[:500],
                                "source": "instagram",
                                "timestamp": datetime.now().isoformat(),
                                "location": location,
                                "url": url,
                            })

                    # Also try to get text from any visible captions
                    captions = driver.find_elements(
                        By.CSS_SELECTOR, "span[class*='Caption'], div[class*='caption']"
                    )
                    for caption in captions[:10]:
                        text = caption.text.strip()
                        if len(text) > 15:
                            results.append({
                                "text": text[:500],
                                "source": "instagram",
                                "timestamp": datetime.now().isoformat(),
                                "location": location,
                                "url": url,
                            })

                    time.sleep(2)

                except Exception as e:
                    print(f"Instagram hashtag #{tag} error: {e}")
                    continue

        except Exception as e:
            print(f"Instagram scraper error: {e}")
        finally:
            try:
                driver.quit()
            except Exception:
                pass

        return results
