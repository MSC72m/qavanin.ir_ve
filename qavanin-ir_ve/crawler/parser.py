import logging
from scrapy.selector import Selector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HTMLLinkExtractor:
    """
    A class for extracting links from HTML content.

    This class uses Scrapy's Selector to parse HTML and extract specific links.
    """

    def __init__(self):
        self.urls = []

    def extract_links(self, html_content) -> list:
        """
        Extract links from the provided HTML content.

        Args:
            html_content (str): The HTML content to parse.

        Returns:
            list: A list of extracted URLs.
        """
        selector = Selector(text=html_content)
        hrefs = selector.xpath(
            '//div[@id="main"]//table[@class="border-list table table-striped table-hover"]//td['
            '@class="text-justify"]/a/@href').getall()
        self.urls.extend(hrefs)
        return self.urls

    def get_urls(self):
        """
        Get the list of extracted URLs.

        Returns:
            list: The list of URLs extracted so far.
        """
        return self.urls


class HTMLParserEachPage:
    """
    A class for parsing individual HTML pages and extracting specific text content.

    This class uses Scrapy's Selector to parse HTML and extract text from specific elements.
    """

    def __init__(self):
        self.pages = []

    def extract_text(self, html_content: object):
        """
        Extract text from the provided HTML content.

        This method looks for <p> tags with the class 'SecTex' and extracts their text content.

        Args:
            html_content (object): The HTML content to parse.

        Returns:
            str: The extracted text, joined with double newlines for Markdown compatibility.
        """
        try:
            selector = Selector(text=html_content, type="html")

            logger.info("Extracting text from HTML content.")

            p_tags = selector.xpath('//p[contains(@class, "SecTex")]//text()').getall()

            if not p_tags:
                logger.warning("No <p> tags with class 'SecTex' were found.")
            else:
                logger.info(f"Found {len(p_tags)} <p> tags with class 'SecTex'.")
            # two \n's are needed because Markdown requires it
            extracted_text = '\n\n'.join(p_tags)
            self.pages.append(extracted_text)

            return extracted_text

        except AttributeError as e:
            logger.error(f"An error occurred: {e}")
            return ""

    def get_pages(self):
        """
        Get the list of extracted page contents.

        Returns:
            list: The list of page contents extracted so far.
        """
        return self.pages