import logging
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import time
from parser import HTMLLinkExtractor, HTMLParserEachPage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebDriverSetup(ABC):
    @abstractmethod
    def create_driver(self):
        pass


class ChromeDriverSetup(WebDriverSetup):
    def create_driver(self):
        options = Options()
        options.headless = True
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1920,1080")

        try:
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except WebDriverException as e:
            logger.error(f"Could not initialize the WebDriver: {e}")
            raise


class WebScraper:
    def __init__(self, driver_setup: WebDriverSetup, timeout: int = 40, retries: int = 3):
        self.driver_setup = driver_setup
        self.timeout = timeout
        self.driver = None
        self.retries = retries

    def __enter__(self):
        self.open_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_driver()

    def open_driver(self):
        if self.driver is None:
            self.driver = self.driver_setup.create_driver()

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def get_page_content(self, url):
        for attempt in range(self.retries):
            try:
                self.open_driver()
                self.driver.get(url)
                time.sleep(4)
                WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                return self.driver.page_source
            except WebDriverException as e:
                logger.warning(f"Error fetching {url}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
            time.sleep(4)

        logger.error(f"Failed to fetch {url} after {self.retries} attempts")
        return None


class Scraper:
    def __init__(self, web_scraper: WebScraper, link_parser: HTMLLinkExtractor, page_parser: HTMLParserEachPage):
        self.web_scraper = web_scraper
        self.link_parser = link_parser
        self.page_parser = page_parser

    def scrape_main_pages(self, url_template: str, max_pages: int, page_number: int, item_in_page: int):
        content_list = []
        for _ in range(max_pages):
            url = url_template.format(page_number, page_number, item_in_page)
            content = self.web_scraper.get_page_content(url)
            if content:
                content_list.append(content)
                page_number += 1
            else:
                logger.warning(f"Skipping page {page_number} due to error")
        return content_list

    def extract_links(self, content_list):
        all_links = []
        for content in content_list:
            links = self.link_parser.extract_links(content)
            all_links.extend(links)
        return all_links

    def scrape_pages(self, url_template: str, ids: list):
        pages_html = []
        for _id in ids:
            url = url_template.format(_id)
            content = self.web_scraper.get_page_content(url)
            if content:
                parsed_content = self.page_parser.extract_text(content)
                if parsed_content:  # Only append if content was actually extracted
                    pages_html.append(parsed_content)
            else:
                logger.warning(f"Skipping page with ID {_id} due to error")
        return pages_html


