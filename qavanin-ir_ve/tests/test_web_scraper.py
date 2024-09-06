import pytest
from unittest.mock import Mock, patch
from crawler.web_scraper import ChromeDriverSetup, WebScraper, Scraper

@pytest.fixture
def mock_driver():
    """Fixture that returns a mock WebDriver instance."""
    return Mock()

@pytest.fixture
def mock_parser():
    """Fixture that returns a mock parser instance."""
    return Mock()

@pytest.fixture
def chrome_driver_setup():
    """Fixture that returns a ChromeDriverSetup instance."""
    return ChromeDriverSetup()

@pytest.fixture
def web_scraper(mock_driver, chrome_driver_setup):
    """Fixture that returns a WebScraper instance with a mock driver."""
    with patch("web_scraper.ChromeDriverSetup.create_driver", return_value=mock_driver):
        return WebScraper(chrome_driver_setup)

@pytest.fixture
def scraper(web_scraper, mock_parser):
    """Fixture that returns a Scraper instance with a mock web scraper and parser."""
    return Scraper(web_scraper, mock_parser, mock_parser)

def test_chrome_driver_setup(chrome_driver_setup):
    """Test that the ChromeDriverSetup class creates a WebDriver instance correctly."""
    driver = chrome_driver_setup.create_driver()
    assert driver is not None

def test_web_scraper_get_page_content(web_scraper, mock_driver):
    """Test that the WebScraper class can fetch page content successfully."""
    mock_driver.page_source = "<html><body>Test</body></html>"
    content = web_scraper.get_page_content("https://example.com")
    assert content == "<html><body>Test</body></html>"

def test_scraper_scrape_main_pages(scraper, web_scraper, mock_driver):
    """Test that the Scraper class can scrape multiple pages correctly."""
    mock_driver.page_source = "<html><body>Test</body></html>"
    content_list = scraper.scrape_main_pages("https://example.com/page/{}/{}", 1, 2, 10)
    assert len(content_list) == 2

def test_scraper_extract_links(scraper, mock_parser):
    """Test that the Scraper class can extract links correctly."""
    mock_parser.extract_links.return_value = ["https://example.com/page1", "https://example.com/page2"]
    content_list = ["<html><body>Test</body></html>"]
    links = scraper.extract_links(content_list)
    assert len(links) == 2

def test_scraper_scrape_pages(scraper, web_scraper, mock_driver, mock_parser):
    """Test that the Scraper class can scrape individual pages correctly."""
    mock_driver.page_source = "<html><body>Test</body></html>"
    mock_parser.extract_text.return_value = "Test"
    pages_html = scraper.scrape_pages("https://example.com/page/{}", [1, 2])
    assert len(pages_html) == 2
