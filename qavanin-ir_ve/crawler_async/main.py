from .web_scraper import (
    WebScraper,
    Scraper,
    HTMLParserEachPage,
    HTMLLinkExtractor,
)
import logging
import time

# from data_processing.text_cleaner import convert_to_markdown
# from database.db_oprations import insert_document, get_document_count
# from database.models import init_db
# from data_processing.vectorizer import generate_embeddings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """
    Main function to orchestrate the web scraping process.

    This function initializes the necessary components, performs the web scraping,
    processes the scraped data, and stores it in the database.
    """

    try:
        logger.info("Start Crawling")
        start = time.time()
        # total links to load in each page
        item_in_page = 25
        # first page that crawling will started at
        start_page = 1
        # last page which will be scraped. (from start_page to last_page)
        last_page = 2
        main_url_template = "https://qavanin.ir/?PageNumber={}&page={}&size={}"
        law_url_template = "https://qavanin.ir{}"
        web_scraper = WebScraper()
        scraper = Scraper(web_scraper, HTMLLinkExtractor(), HTMLParserEachPage())

        content_list = scraper.scrape_main_pages(
            main_url_template, start_page, last_page, item_in_page
        )
        ids = scraper.extract_links(content_list)
        pages_html = scraper.scrape_pages(law_url_template, ids)

        # Process and store the scraped content
        # for page in pages_html:
        #     content = convert_to_markdown(page)
        #     embeds = generate_embeddings(page)
        # insert_document(content, embeds)

    except Exception as e:
        logger.error(f"error on crawl : {e}")
    # with WebScraper(driver_setup) as web_scraper:
    #     scraper = Scraper(web_scraper, HTMLLinkExtractor(), HTMLParserEachPage())

    #     content_list = scraper.scrape_main_pages(
    #         main_url_template, start_page, last_page, item_in_page
    #     )
    #     ids = scraper.extract_links(content_list)
    #     pages_html = scraper.scrape_pages(law_url_template, ids)

    #     # Process and store the scraped content
    #     for page in pages_html:
    #         content = convert_to_markdown(page)
    #         embeds = generate_embeddings(page)
    #         insert_document(content, embeds)

    end = time.time()
    total_time = end - start
    logger.info(f"Total scraped links (IDs extracted): {len(ids)}")
    logger.info(f"Scraped {last_page} pages, each page contained {item_in_page} items")
    logger.info(f"Scraped HTML of {len(pages_html)} pages")
    logger.info(f"Total time: {total_time:.2f} seconds")
    # logger.info(f"total documents in db: {get_document_count()}")
    return None


if __name__ == "__main__":
    main()
