import logging
from scrapy.selector import Selector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HTMLLinkExtractor:
    def __init__(self):
        self.urls = []

    def extract_links(self, html_content) -> list:
        selector = Selector(text=html_content)
        hrefs = selector.xpath(
            '//div[@id="main"]//table[@class="border-list table table-striped table-hover"]//td['
            '@class="text-justify"]/a/@href').getall()
        self.urls.extend(hrefs)
        return self.urls

    def get_urls(self):
        return self.urls


class HTMLParserEachPage:
    def __init__(self):
        self.pages = []

    def extract_text(self, html_content: object):
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

            return extracted_text  # Return only the newly extracted text

        except AttributeError as e:
            logger.error(f"An error occurred: {e}")
            return ""  # Return an empty string in case of an error

    def get_pages(self):
        return self.pages
