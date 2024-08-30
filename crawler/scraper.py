from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
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

        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

class WebScraper:
    def __init__(self, driver_setup: WebDriverSetup, timeout: int = 30):
        self.driver_setup = driver_setup
        self.timeout = timeout
        self.driver = self.driver_setup.create_driver()

    def get_page_content(self, url):
        try:
            self.driver.get(url)
            time.sleep(8)
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return self.driver.page_source
        finally:
            self.driver.quit()




def main():
    driver_setup = ChromeDriverSetup()
    scraper = WebScraper(driver_setup)
    main_url = 'https://qavanin.ir'
    content = scraper.get_page_content(main_url)
    with open('text.txt', 'w') as f:
        f.write(content)
    parser = HTMLLinkExtractor()
    links = parser.extract_links(content)
    urls = parser.get_urls()
    print(urls)

if __name__ == "__main__":
    main()
