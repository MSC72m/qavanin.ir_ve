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
| 100        |     28.7         |     0.71   |
| 200        |     101.4        |     0.49   |
| 300        |     115.3        |     0.61   |
| 400        |     194.9        |     0.51   |
| 500        |     269.2        |     0.46   |

