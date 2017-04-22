import multiprocessing
from Queue import Empty
from multiprocessing import Pool, Manager
from urlparse import urlsplit, urlunsplit

import requests
from requests import RequestException

from crawler.html_resources_parser import HTMLResourcesParser


def crawl_url(url):
    '''Get html from the specified url and extract all links and resources referenced
    
    :param url: The url to get html from
    :return: Returns a tuple (links, resources) of links and resources found
    '''
    parser = HTMLResourcesParser(url)
    try:
        response = requests.get(url)
        response.raise_for_status()
        html = response.text
        return parser.extract_links_and_assets(html)
    except RequestException, e:
        print "Could not open url: " + url + " (" + str(e) + ")"
        raise


def crawler(domain, urls_to_crawl, crawled, sitemap, assets, invalid_urls):
    '''Crawl urls provided in a queue and populate a sitemap and dictionary of assets per page
    
    The crawler visits each url and identifies links and resources from the page. Each link is validated and the 
    header is checked. Any links to html pages in the same domain are added to the queue to be crawled. Any invalid 
    urls are added to a list to avoid attempting to validate them again. All links and resources area added to the 
    assets dictionary. 
    
    :param domain: The domain to which the crawler is restricted
    :param urls_to_crawl: A queue containing urls which should be visited by the crawler
    :param crawled: A list containing urls already added to urls_to_crawl
    :param sitemap: A dictionary mapping pages to urls referenced by the page
    :param assets: A dictionary mapping pages to assets references by the page
    :param invalid_urls: A list containing urls which have been identified as invalid
    '''
    while True:
        try:
            url = urls_to_crawl.get(timeout=1)
        except Empty:
            break
        try:
            (links, resources) = crawl_url(url)
        except RequestException:
            continue

        page_assets = resources
        page_links = set()

        for link in links:
            split_link = urlsplit(link)
            if split_link.scheme in {"http", "https"}:
                # Construct clean url to avoid repeatedly visiting different formats of the same page
                new_url = urlunsplit((split_link.scheme, split_link.netloc, split_link.path.strip("/"), None, None))
                if new_url not in page_links.union(invalid_urls):
                    try:
                        response = requests.head(new_url)
                        response.raise_for_status()
                        headers = response.headers
                        # If content type is not present in header, assume it is html
                        if "Content-Type" not in headers or "text/html" in headers.get("Content-Type"):
                            if domain == split_link.netloc:
                                page_links.add(new_url)
                                if new_url not in crawled:
                                    crawled += [new_url]
                                    urls_to_crawl.put(new_url)
                        # Ensure all links are added to the page assets
                        page_assets.add(new_url)
                    except RequestException, e:
                        invalid_urls += [new_url]
                        print "Could not open url: " + new_url + "(" + e.message + ")"

        sitemap[url] = page_links
        assets[url] = page_assets


def print_results(sitemap, assets):
    '''Prints formatted results for sitemap and assets to stdout
    
    :param sitemap: A dictionary mapping pages to urls referenced by the page
    :param assets: A dictionary mapping pages to assets references by the page
    '''
    print "Sitemap"
    for url in sorted({url for links in sitemap.values() for url in links}):
        print url
    print "\n"
    print "Assets"
    for url in sorted(assets.keys()):
        print "Assets on " + url
        for asset in sorted(assets[url]):
            print asset
        print "\n"


if __name__ == '__main__':
    logger = multiprocessing.log_to_stderr()

    manager = Manager()

    # Create sitemap and assets dictionaries to hold results
    sitemap = manager.dict()
    assets = manager.dict()

    domain = "yoyowallet.com"

    # Create queue which will be populated with urls as they are found by the crawler
    urls_to_crawl = manager.Queue()
    urls_to_crawl.put("http://" + domain)

    crawled = manager.list(["http://" + domain])  # List of urls already added to the queue to be crawled

    invalid_urls = manager.list()  # List of invalid urls to avoid repeatedly requesting from them

    pool = Pool(4, crawler, (domain, urls_to_crawl, crawled, sitemap, assets, invalid_urls))

    pool.close()
    pool.join()

    print_results(sitemap, assets)
