from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json

def scrape_reel_metadata(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector("script[type='application/ld+json']")
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        script_tag = soup.find("script", {"type": "application/ld+json"})
        metadata = json.loads(script_tag.string)
        browser.close()
        return {
            "author": metadata.get("author", {}).get("name"),
            "caption": metadata.get("description"),
            "views": metadata.get("interactionStatistic", {}).get("userInteractionCount")
        }

print(scrape_reel_metadata("https://www.instagram.com/reel/DLMa69noWxC/"))
