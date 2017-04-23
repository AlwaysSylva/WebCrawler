from Queue import Queue

import pytest
import requests
from requests import Response, RequestException

import web_crawler
from crawler.html_resources_parser import HTMLResourcesParser


@pytest.fixture
def monkeypatch_requests_get(monkeypatch):
    def mockget(url):
        response = Response()
        response.status_code = 200
        response._content = 'html'
        return response

    monkeypatch.setattr(requests, "get", mockget)


@pytest.fixture
def monkeypatch_requests_get_invalid(monkeypatch):
    def mockget(url):
        response = Response()
        response.status_code = 404
        response._content = 'html'
        return response

    monkeypatch.setattr(requests, "get", mockget)


@pytest.fixture
def monkeypatch_requests_head(monkeypatch):
    def mockhead(url):
        response = Response()
        response.status_code = 200
        response.headers = {"Content-Type": "text/html"}
        return response

    monkeypatch.setattr(requests, "head", mockhead)


@pytest.fixture(autouse=True)
def monkeypatch_html_resources_parser(monkeypatch):
    def mockextract(self, html):
        links = {"http://test.com/link"}
        resources = {"http://test.com/resource"}
        return (links, resources)

    monkeypatch.setattr(HTMLResourcesParser, "extract_links_and_assets", mockextract)


def test_crawl_url_valid(monkeypatch_requests_get):
    (links, resources) = web_crawler.crawl_url("http://test.com")
    assert links == {"http://test.com/link"}
    assert resources == {"http://test.com/resource"}


def test_crawl_url_invalid(monkeypatch_requests_get_invalid):
    with pytest.raises(RequestException):
        (links, resources) = web_crawler.crawl_url("http://test.com")


def test_crawler(monkeypatch_requests_get, monkeypatch_requests_head):
    domain = "test.com"
    urls_to_crawl = Queue()
    urls_to_crawl.put("http://" + domain)
    sitemap = {}
    assets = {}
    web_crawler.crawler(domain, urls_to_crawl, [], sitemap, assets, [])
    assert sitemap == {"http://test.com": {"http://test.com/link"},
                       "http://test.com/link": {"http://test.com/link"}}
    assert assets == {"http://test.com": {"http://test.com/link", "http://test.com/resource"},
                      "http://test.com/link": {"http://test.com/link", "http://test.com/resource"}}
