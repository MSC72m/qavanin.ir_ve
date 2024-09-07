# Crawler (Async) for Qavanin Pages
Implement crawler with ability to handle async requests to website.



## Statistics

Here is running statistics to compare with other crawler scenarios.

### `scripts/crawl_pages.py`

Total time of crawl and extract all links of 161 pages: 149.27 seconds

### `scripts/crawl_qavanin.py`
 Statistic reported based on different chunk sizes (number of asynchronous requests):

| chunk size | error count (avg)| error rate |
|------------|------------------|------------|
| 100        |     28.7         |     71.3   |
| 200        |     101.4        |     98.6   |
| 300        |     115.3        |     184.7  |
| 400        |     194.9        |     205.1  |
| 500        |     269.2        |     230.8  |

