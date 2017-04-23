# WebCrawler
Crawl a specified website to produce a sitemap and list of assets

# Installation
The crawler is written for [Python 2.7](https://www.python.org/). Additional packages should be installed from the provided [requirements.txt](requirements.txt) file:
```
pip install -r requirements.txt
```

# Usage
The program can be executed from the command line using the web_crawler.py file.
```
python web_crawler.py [-h] [--workers [WORKERS]] domain

positional arguments:
  domain  The domain to crawl (e.g. yoyowallet.com)

optional arguments:
  -h, --help  Show this help message and exit
  --workers [WORKERS]  The number of workers to start (default = 8)
```
## Example
```
python web_crawler.py yoyowallet.com
```

# Tests
Test are written using [pytest](https://docs.pytest.org/) and executed with:
```
python -m pytest
```
