import pytest
from crawler.parser import HTMLLinkExtractor, HTMLParserEachPage

@pytest.fixture
def link_extractor():
    """Fixture that returns an HTMLLinkExtractor instance."""
    return HTMLLinkExtractor()

@pytest.fixture
def page_parser():
    """Fixture that returns an HTMLParserEachPage instance."""
    return HTMLParserEachPage()

@pytest.mark.parametrize("html_content, expected_urls", [
    ("<html><body><div id='main'><table class='border-list table table-striped table-hover'><td class='text-justify'><a href='https://example.com/page1'>Page 1</a></td><td class='text-justify'><a href='https://example.com/page2'>Page 2</a></td></table></div></body></html>", ["https://example.com/page1", "https://example.com/page2"]),
    ("<html><body><div id='main'><table class='border-list table table-striped table-hover'><td class='text-justify'><a href='https://example.com/page3'>Page 3</a></td></table></div></body></html>", ["https://example.com/page3"]),
])
def test_html_link_extractor(link_extractor, html_content, expected_urls):
    """Test that the HTMLLinkExtractor class can extract links from HTML content correctly."""
    urls = link_extractor.extract_links(html_content)
    assert urls == expected_urls

@pytest.mark.parametrize("html_content, expected_text", [
    ("<html><body><p class='SecTex'>This is a test.</p><p class='SecTex'>This is another test.</p></body></html>", "This is a test.\n\nThis is another test."),
    ("<html><body><p class='SecTex'>This is a test.</p></body></html>", "This is a test."),
    ("<html><body><p>This is not a test.</p></body></html>", ""),
])
def test_html_parser_each_page(page_parser, html_content, expected_text):
    """Test that the HTMLParserEachPage class can extract text from HTML content correctly."""
    text = page_parser.extract_text(html_content)
    assert text == expected_text
