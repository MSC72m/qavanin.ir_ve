from ..crawler.web_scraper import ChromeDriverSetup, WebScraper, Scraper, HTMLParserEachPage, HTMLLinkExtractor
import logging
import time
from ..data_processing.text_cleaner import enhanced_convert_to_markdown
from ..database.db_oprations import insert_document, get_document_count
from ..database.models import init_db, check_pgvector_extension
from ..data_processing.vectorizer import generate_embeddings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """
    Temporarily saving scraped pages to 'text.txt'. This is needed for the implementation of the data cleaning process,
    which includes transforming HTML tags into Markdown format. Next steps involve implementing the VE (validation and
    enrichment) part, and subsequently saving both the VE output and the cleaned Markdown content into a PostgreSQL database.
    There is still a lot of work to be done.
    """
    global driver_setup
    start = time.time()
    item_in_page = 50
    start_page = 1
    last_page = 7
    main_url_template = 'https://qavanin.ir/?PageNumber={}&page={}&size={}'
    law_url_template = "https://qavanin.ir{}"
    try:
        driver_setup = ChromeDriverSetup()
    except Exception as e:
        logger.error(f"error initializing driver: {e}")
    with WebScraper(driver_setup) as web_scraper:
        scraper = Scraper(web_scraper, HTMLLinkExtractor(), HTMLParserEachPage())

        content_list = scraper.scrape_main_pages(main_url_template, start_page, last_page, item_in_page)
        ids = scraper.extract_links(content_list)
        pages_html = scraper.scrape_pages(law_url_template, ids)

        # saving the html into a text file for later on. TEMP
        for page in pages_html:
            content = enhanced_convert_to_markdown(page)
            embeds = generate_embeddings(page)
            insert_document(content, embeds)

    end = time.time()
    total_time = end - start
    logger.info(f"Total scraped links (IDs extracted): {len(ids)}")
    logger.info(f"Scraped {last_page} pages, each page contained {item_in_page} items")
    logger.info(f"Scraped HTML of {len(pages_html)} pages")
    logger.info(f"Total time: {total_time:.2f} seconds")
    logger.info(f"total documents in db: {get_document_count()}")
    return None


if __name__ == "__main__":
    main()
