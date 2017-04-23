from Queue import Empty
from multiprocessing import Manager
from urlparse import urlsplit, urlunsplit

import requests
from requests import RequestException

from html_resources_parser import HTMLResourcesParser


class Crawler(object):
    WAITING_STATUS = "waiting"
    PROCESSING_STATUS = "processing"

    def __init__(self, domain):
        manager = Manager()
        self.worker_register = manager.dict()

        # Create sitemap and assets dictionaries to hold results
        self._sitemap = manager.dict()
        self._assets = manager.dict()

        self._domain = domain

        # Create queue which will be populated with urls as they are found by the crawler
        self._urls_to_crawl = manager.Queue()
        self._urls_to_crawl.put("http://" + domain)

        self._crawled = manager.list(["http://" + domain])  # List of urls already added to the queue to be crawled

        self._invalid_urls = manager.list()  # List of invalid urls to avoid repeatedly requesting from them

    @property
    def sitemap(self):
        return self._sitemap._getvalue()

    @property
    def assets(self):
        return self._assets._getvalue()

    def workers_processing(self):
        return self.PROCESSING_STATUS in self.worker_register.values()

    def crawl_url(self, url):
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

    def is_http(self, split_link):
        return split_link.scheme in {"http", "https"}

    def start_crawler(self):
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
        worker_id = len(self.worker_register)+1
        self.worker_register[worker_id] = self.WAITING_STATUS

        while True:
            try:
                self.worker_register[worker_id] = self.WAITING_STATUS
                url = self._urls_to_crawl.get(timeout=1)
            except Empty:
                if self.workers_processing():
                    continue
                else:
                    break
            self.worker_register[worker_id] = self.PROCESSING_STATUS

            try:
                (links, resources) = self.crawl_url(url)
            except RequestException:
                continue

            page_assets = resources
            page_links = set()

            for link in links:
                split_link = urlsplit(link)
                # Construct clean url to avoid repeatedly visiting different formats of the same page
                new_url = urlunsplit((split_link.scheme, split_link.netloc, split_link.path.strip("/"), None, None))
                if self.is_http(split_link) and new_url not in page_links.union(self._invalid_urls):
                    try:
                        response = requests.head(new_url)
                        response.raise_for_status()
                        headers = response.headers
                        # If content type is not present in header, assume it is html
                        if "Content-Type" not in headers or "text/html" in headers.get("Content-Type"):
                            if self._domain == split_link.netloc:
                                page_links.add(new_url)
                                if new_url not in self._crawled:
                                    self._crawled += [new_url]
                                    self._urls_to_crawl.put(new_url)
                        # Ensure all links are added to the page assets
                        page_assets.add(new_url)
                    except RequestException, e:
                        self._invalid_urls += [new_url]
                        print "Could not open url: " + new_url + "(" + str(e) + ")"

            self._sitemap[url] = page_links
            self._assets[url] = page_assets