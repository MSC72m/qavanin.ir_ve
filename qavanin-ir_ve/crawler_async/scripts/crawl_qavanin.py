import asyncio
import aiohttp
from crawler_async.core import BASE_QAVANIN_URL, get_hash
import json
import glob
import time, random
import logging
import time
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QavaninPageCrawler:
    def __init__(self, chunk_size: int = 50):
        self.chunk_size = chunk_size
        self.files: list[str] = glob.glob("./files/qavanin/*.html")
        self.exists: set[str] = set(
            [file.split("/")[-1].split(".html")[0] for file in self.files]
        )
        print(list(self.exists)[:5])
        with open("./files/links.txt", "r", encoding="utf-8") as f:
            self.data: list[dict] = [x.strip() for x in f.readlines()]
        self.pages: list[str] = [
            x.split("IDS=")[-1]
            for x in self.data
            if x.split("IDS=")[-1] not in self.exists
        ]
        print(self.pages[:4])
        raise Exception()
        self.chunked_pages: list[list[str]] = [
            self.pages[i : i + self.chunk_size]
            for i in range(0, len(self.pages), self.chunk_size)
        ]

    async def get_page_async(
        self, url: str, headers: dict = {}, payload: dict = {}
    ) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, data=payload) as response:
                return await response.text()

    async def handle_page(self, url: str, headers: dict = {}) -> str:
        content: str = await self.get_page_async(url, headers)

        if "Error 502" in content:
            print("page error")
            return None
            # n=random.randint(0,3)
            # time.sleep(n)
            # content = await self.get_page_async(url, headers)
        if "error-section__title" in content:
            hash: str = get_hash(content)
            if not hash:
                print("hash error")
                return None
            headers = {"cookie": f"__arcsjs={hash};"}
            content = await self.get_page_async(url, headers)
        return content

    async def main(self) -> None:
        # for chunk in self.chunked_pages:
        for chunk in self.chunked_pages:  # todo: remove in production
            errors = []
            tasks = [self.handle_page(BASE_QAVANIN_URL + page) for page in chunk]
            responses = await asyncio.gather(*tasks)

            for page, response in tqdm(zip(chunk, responses)):

                if response and "treeText" in response:
                    with open(
                        f"./files/qavanin/{page}.html", "w", encoding="utf-8"
                    ) as f:
                        f.write(response)
                    continue
                else:
                    errors.append(page)
                    continue
            print("Errors count:", len(errors))
            with open(
                f"./files/errors_{self.chunk_size}.txt", "a", encoding="utf-8"
            ) as f:
                f.write(",".join(errors) + "\n")

    def run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.main())
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":

    logger.info("Start Crawling Qavanin")
    start = time.time()

    crawler = QavaninPageCrawler(chunk_size=300)
    print("total qavanin:", len(crawler.pages))
    crawler.run()
    end = time.time()
    total_time = end - start
    logger.info(f"Total time: {total_time:.2f} seconds")
