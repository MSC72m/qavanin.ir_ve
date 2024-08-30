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


def main():
    start = time.time()
    driver_setup = ChromeDriverSetup()
    scraper = WebScraper(driver_setup)
    item_in_page = 50
    max_pages = 100
    page_number = 1
    content_list = []
    total_scraped_links = 0
    main_url_template = 'https://qavanin.ir/?PageNumber={}&page={}&size={}'

    for _ in range(max_pages):
        main_url = main_url_template.format(page_number, page_number, item_in_page)
        try:
            content_list.append(scraper.get_page_content(main_url))
            page_number += 1
        except Exception as e:
            print(f"Skipping page {page_number} due to error: {e}")
            continue

    parser = HTMLLinkExtractor()
    for content in content_list:
        links = parser.extract_links(content)
        for link in links:
            parts = link.split("/Law/TreeText/?IDS=")  # Correctly split each link
            if len(parts) > 1:  # Ensure there's something to extract
                extracted_part = parts[1]  # Change to parts[1] to get the ID part
                print(extracted_part)
                total_scraped_links += 1
    end = time.time()
    total_time = end - start
    print("Total scraped links(IDs extracted): ", total_scraped_links)
    print(f"scraped {max_pages} pages, each page contained {item_in_page} items and it took {total_time // 60}")


if __name__ == "__main__":
    main()
