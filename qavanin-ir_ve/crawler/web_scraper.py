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
from .parser import HTMLLinkExtractor, HTMLParserEachPage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebDriverSetup(ABC):
    """Abstract base class for WebDriver setup."""

    @abstractmethod
    def create_driver(self):
        """Create and return a WebDriver instance."""
        pass


class ChromeDriverSetup(WebDriverSetup):
    """Chrome WebDriver setup implementation."""

    def create_driver(self):
        """
        Create and return a Chrome WebDriver instance with specific options.

        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance.

        Raises:
            WebDriverException: If the WebDriver could not be initialized.
        """
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
    """Manages the web scraping process using Selenium WebDriver."""

    def __init__(self, driver_setup: WebDriverSetup, timeout: int = 40, retries: int = 3):
        """
        Initialize the WebScraper.

        Args:
            driver_setup (WebDriverSetup): The WebDriver setup to use.
            timeout (int): Maximum wait time for page loads (default: 40 seconds).
            retries (int): Number of retries for failed page loads (default: 3).
        """
        self.driver_setup = driver_setup
        self.timeout = timeout
        self.driver = None
        self.retries = retries

    def __enter__(self):
        """Context manager entry point."""
        self.open_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.close_driver()

    def open_driver(self):
        """Open the WebDriver if it's not already open."""
        if self.driver is None:
            self.driver = self.driver_setup.create_driver()

    def close_driver(self):
        """Close the WebDriver if it's open."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def get_page_content(self, url):
        """
        Get the content of a webpage.

        Args:
            url (str): The URL of the page to scrape.

        Returns:
            str: The page source if successful, None otherwise.
        """
        for attempt in range(self.retries):
            try:
                self.open_driver()
                self.driver.get(url)
                time.sleep(3)
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
    """Orchestrates the scraping process using WebScraper and parser classes."""

    def __init__(self, web_scraper: WebScraper, link_parser: HTMLLinkExtractor, page_parser: HTMLParserEachPage):
        """
        Initialize the Scraper.

        Args:
            web_scraper (WebScraper): The WebScraper instance to use.
            link_parser (HTMLLinkExtractor): The link extractor to use.
            page_parser (HTMLParserEachPage): The page parser to use.
        """
        self.web_scraper = web_scraper
        self.link_parser = link_parser
        self.page_parser = page_parser

    def scrape_main_pages(self, url_template: str, start_page:int, last_page: int, item_in_page: int):
        """
        Scrape multiple pages using a URL template.

        Args:
            url_template (str): The URL template to use.
            start_page (int): The first page number to scrape.
            last_page (int): The last page number to scrape.
            item_in_page (int): The number of items per page.

        Returns:
            list: A list of page contents.
        """
        content_list = []
        for page_number in range(start_page, last_page + 1):
            url = url_template.format(page_number, page_number, item_in_page)
            content = self.web_scraper.get_page_content(url)
            if content:
                content_list.append(content)
            else:
                logger.warning(f"Skipping page {page_number} due to error")
        return content_list

    def extract_links(self, content_list):
        """
        Extract links from a list of page contents.

        Args:
            content_list (list): A list of page contents.

        Returns:
            list: A list of extracted links.
        """
        all_links = []
        for content in content_list:
            links = self.link_parser.extract_links(content)
            all_links.extend(links)
        return all_links

    def scrape_pages(self, url_template: str, ids: list):
        """
        Scrape individual pages using a list of IDs.

        :Args:
            url_template (str): The URL template to use.
            ids (list): A list of page IDs to scrape.

        returns: A list of page contents.
        """
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

