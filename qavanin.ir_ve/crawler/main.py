from web_scraper import ChromeDriverSetup, WebScraper, Scraper, HTMLParserEachPage, HTMLLinkExtractor
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """
    Temporarily saving scraped pages to 'text.txt'. This is needed for the implementation of the data cleaning process,
    which includes transforming HTML tags into Markdown format. Next steps involve implementing the VE (validation and
    enrichment) part, and subsequently saving both the VE output and the cleaned Markdown content into a PostgreSQL database.
    There is still a lot of work to be done.
    """
    start = time.time()
    item_in_page = 25
    max_pages = 1
    page_number = 1
    main_url_template = 'https://qavanin.ir/?PageNumber={}&page={}&size={}'
    law_url_template = "https://qavanin.ir/{}"

    driver_setup = ChromeDriverSetup()
    with WebScraper(driver_setup) as web_scraper:
        scraper = Scraper(web_scraper, HTMLLinkExtractor(), HTMLParserEachPage())

        content_list = scraper.scrape_main_pages(main_url_template, max_pages, page_number, item_in_page)
        ids = scraper.extract_links(content_list)
        pages_html = scraper.scrape_pages(law_url_template, ids)
    # saving the html into a text file for later on. TEMP
    with open('text.txt', 'w', encoding='utf-8') as f:
        for item in pages_html:
            f.write(item)
            f.write('\n\n')

    end = time.time()
    total_time = end - start
    logger.info(f"Total scraped links (IDs extracted): {len(ids)}")
    logger.info(f"Scraped {max_pages} pages, each page contained {item_in_page} items")
    logger.info(f"Scraped HTML of {len(pages_html)} pages")
    logger.info(f"Total time: {total_time:.2f} seconds")

    return None


if __name__ == "__main__":
    main()
