# contentscraper.py
import logging
import validators
from playwright.sync_api import sync_playwright
from trafilatura.settings import use_config
import trafilatura
from typing import Callable
import os

# Setup logging
logging.basicConfig(level=logging.INFO)

class PlaywrightFetcher:
    def __init__(self, wait_time: int = 1500):
        self.wait_time = wait_time

    def fetch_html(self, url: str) -> str:
        if not validators.url(url):
            raise ValueError(f"Invalid URL: {url}")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(self.wait_time)
            return page.content()

class TrafilaturaFetcher:
    def fetch_html(self, url: str) -> str:
        downloaded = trafilatura.fetch_url(url)
        return downloaded if downloaded else ""

class ContentScraper:
    def __init__(self, fetch_strategy: Callable[[str], str], config_path: str, include_comments: bool = False, include_links: bool = True):
        self.fetch_strategy = fetch_strategy
        self.config_path = config_path
        self.include_comments = include_comments
        self.include_links = include_links

    def scrape_content(self, url: str) -> str:
        html_content = self.fetch_strategy(url)
        if not html_content:
            return ""
        my_config = trafilatura.settings.use_config(self.config_path)
        return trafilatura.extract(html_content, config=my_config, include_comments=self.include_comments, include_links=self.include_links, url=url, output_format='xml')

    def save_content(self, content: str, file_path: str) -> None:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except Exception as e:
            logging.error(f"Error in save_content: {e}", exc_info=True)

    def file_exists(self, file_path: str) -> bool:
        return os.path.exists(file_path)
            
def main(use_playwright: bool = False):
    config_path = "src/settings.cfg"
    fetcher_class = PlaywrightFetcher if use_playwright else TrafilaturaFetcher
    fetcher = fetcher_class().fetch_html
    scraper = ContentScraper(fetcher, config_path)

    try:
        with open("input_urls.txt", "r") as file:
            urls = [url.strip() for url in file]

        for url in urls:
            file_path = f"data/content_{url.split('//')[-1].replace('/', '_')}.xml"
            if os.path.exists(file_path):  # Check if file already exists
                logging.info(f"File already exists, skipping: {file_path}")
                continue  # Skip to the next URL

            try:
                content = scraper.scrape_content(url)
                if content:
                    scraper.save_content(content, file_path)
                    logging.info(f"Content saved to {file_path}")
                else:
                    logging.warning(f"No content for URL: {url}")
            except Exception as e:
                logging.error(f"Error processing URL {url}: {e}", exc_info=True)
    except Exception as e:
        logging.error(f"Error in main: {e}", exc_info=True)



if __name__ == "__main__":
    main(use_playwright=True)  # Change this to True to use Playwright for js sites