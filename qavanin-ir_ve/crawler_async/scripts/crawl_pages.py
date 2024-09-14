import asyncio
from crawler_async.core import URL_TEMPLATE, get_hash, get_page_async
from tqdm import tqdm
import lxml.html
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_page(url, headers={}):
    content = await get_page_async(url, headers)
    if "error-section__title" in content:
        hash = get_hash(content)
        if not hash:
            logger.error("hash error")
            return None
        headers = {"cookie": f"__arcsjs={hash};"}
        content = await get_page_async(url, headers)
    return content


async def main(start_page=1, last_page=2):
    links = []
    pages = range(start_page, last_page + 1)
    chunked_pages = [pages[i : i + 50] for i in range(0, len(pages), 50)]
    for chunk in chunked_pages:
        tasks = [handle_page(URL_TEMPLATE.format(page=page)) for page in chunk]
        responses = await asyncio.gather(*tasks)

        for page, response in tqdm(zip(chunk, responses)):
            if response is None:
                logger.error("Error")
                continue
            tree = lxml.html.fromstring(response)
            urls = tree.xpath(
                '//div[@id="main"]//table[@class="border-list table table-striped table-hover"]//td[@class="text-justify"]/a/@href'
            )
            links.extend(urls)
            with open(f"./files/pages/{page}.html", "w", encoding="utf-8") as f:
                f.write(response)
    with open("./files/links.txt", "w", encoding="utf-8") as f:
        # for link in links:
        #     f.write(f"{link}\n")
        f.write("\n".join(links))


if __name__ == "__main__":
    
    logger.info("Start Crawling")
    start = time.time()
    start_page = 1
    last_page = 161
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main(start_page, last_page))
    except KeyboardInterrupt:
        pass

    end = time.time()
    total_time = end - start
    logger.info(f"Total time: {total_time:.2f} seconds")
