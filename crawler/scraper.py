from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from parser import HTMLLinkExtractor
import time


class WebDriverSetup(ABC):
    @abstractmethod
    def create_driver(self):
        pass


class ChromeDriverSetup(WebDriverSetup):
    def create_driver(self):
        options = Options()
        options.headless = True  # Run in headless mode
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
            print("Could not initialize the WebDriver. Please check your setup.", e)
            raise


class WebScraper:
    def __init__(self, driver_setup: WebDriverSetup, timeout: int = 40, retries: int = 3):
        self.driver_setup = driver_setup
        self.timeout = timeout
        self.driver = None
        self.retries = retries

    def open_driver(self):
        if self.driver is None:
            self.driver = self.driver_setup.create_driver()

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None  # Reset the driver to None after quitting

    def get_page_content(self, url):
        attempt = 0
        while attempt < self.retries:
            try:
                self.open_driver()
                self.driver.get(url)
                time.sleep(7)
                WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                return self.driver.page_source
            except WebDriverException as e:
                print(f"Error fetching {url}: {e}")
                attempt += 1
                time.sleep(4)
            except Exception as e:
                print(f"Unexpected error: {e}")
                attempt += 1
                time.sleep(4)
            finally:
                if attempt == self.retries:
                    self.close_driver()
        raise Exception(f"Failed to fetch page content after {self.retries} attempts")


def scrape_main_page_urls(main_url_template: str, max_pages: int, page_number: int, item_in_page: int,
                          scraper: WebScraper):
    content_list = []
    for _ in range(max_pages):
        main_url = main_url_template.format(page_number, page_number, item_in_page)
        try:
            content_list.append(scraper.get_page_content(main_url))
            page_number += 1
        except Exception as e:
            print(f"Skipping page {page_number} due to error: {e}")
            continue
    return content_list


def scrape_pages(law_url_template: str, ids: list, scraper: WebScraper, page_number: int):
    pages_html = []
    for _id in ids:
        main_url = law_url_template.format(_id)
        try:
            pages_html.append(scraper.get_page_content(main_url))

        except Exception as e:
            print(f"Skipping page {page_number} due to error: {e}")
            continue
    return pages_html


def extract_links(parser: HTMLLinkExtractor, content_list: list, ids: list, total_scraped_links: int):
    global extracted_part
    for content in content_list:
        links = parser.extract_links(content)
        for link in links:
            parts = link.split("/Law/TreeText/?IDS=")  # Correctly split each link
            if len(parts) > 1:  # Ensure there's something to extract
                extracted_part = parts[1]  # Change to parts[1] to get the ID part
                ids.append(extracted_part)
                total_scraped_links += 1
    return extracted_part, total_scraped_links, ids


def main():
    start = time.time()
    item_in_page = 25
    max_pages = 1
    page_number = 1
    total_scraped_links = 0
    ids = []
    main_url_template = 'https://qavanin.ir/?PageNumber={}&page={}&size={}'
    law_url_template = "https://qavanin.ir/Law/TreeText/?IDS={}"
    driver_setup = ChromeDriverSetup()
    scraper = WebScraper(driver_setup)
    content_list = scrape_main_page_urls(main_url_template, max_pages, page_number, item_in_page, scraper)
    parser = HTMLLinkExtractor()
    extracted_parts, total_scraped_links, ids = extract_links(parser, content_list, ids, total_scraped_links)
    pages_html = scrape_pages(law_url_template, ids, scraper, page_number)
    for page in pages_html:
        with open(f"text.txt", "a") as f:
            f.write(page)
    end = time.time()
    total_time = end - start
    print("Total scraped links(IDs extracted): ", total_scraped_links)
    print(f"scraped {max_pages} pages, each page contained {item_in_page} items")
    print(f"scraped html of {len(pages_html)}")
    print(f"total time: {total_time} seconds")


if __name__ == "__main__":
    main()
