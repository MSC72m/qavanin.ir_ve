from scrapy.selector import Selector

class HTMLLinkExtractor:
    def __init__(self):
        self.urls = []

    def extract_links(self, html_content):
        selector = Selector(text=html_content)
        hrefs = selector.xpath('//div[@id="main"]//table[@class="border-list table table-striped table-hover"]//td[@class="text-justify"]/a/@href').getall()
        self.urls.extend(hrefs)
        return self.urls  # Changed from yield to return

    def get_urls(self):
        return self.urls
