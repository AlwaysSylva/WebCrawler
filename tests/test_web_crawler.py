import pytest
import requests
from requests import Response, RequestException

from crawler.crawler import Crawler
from crawler.html_resources_parser import HTMLResourcesParser


@pytest.fixture
def crawler():
    return Crawler("test.com")


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


@pytest.fixture
def monkeypatch_requests_head_invalid(monkeypatch):
    def mockhead(url):
        response = Response()
        response.status_code = 404
        return response

    monkeypatch.setattr(requests, "head", mockhead)


@pytest.fixture
def monkeypatch_requests_head_non_html(monkeypatch):
    def mockhead(url):
        response = Response()
        response.status_code = 200
        response.headers = {"Content-Type": "text/json"}
        return response

    monkeypatch.setattr(requests, "head", mockhead)


@pytest.fixture
def monkeypatch_requests_head_no_content_type(monkeypatch):
    def mockhead(url):
        response = Response()
        response.status_code = 200
        response.headers = {}
        return response

    monkeypatch.setattr(requests, "head", mockhead)


@pytest.fixture(autouse=True)
def monkeypatch_html_resources_parser(monkeypatch):
    def mockextract(self, html):
        links = {"http://test.com/link"}
        resources = {"http://test.com/resource"}
        return (links, resources)

    monkeypatch.setattr(HTMLResourcesParser, "extract_links_and_assets", mockextract)


def test_crawl_url_valid(crawler, monkeypatch_requests_get):
    (links, resources) = crawler.crawl_url("http://test.com")
    assert links == {"http://test.com/link"}
    assert resources == {"http://test.com/resource"}


def test_crawl_url_invalid(crawler, monkeypatch_requests_get_invalid):
    with pytest.raises(RequestException):
        (links, resources) = crawler.crawl_url("http://test.com")


def test_crawler(crawler, monkeypatch, monkeypatch_requests_head):
    def mockcrawl(url):
        links = {"http://test.com/link"}
        resources = {"http://test.com/resource"}
        return links, resources

    monkeypatch.setattr(crawler, "crawl_url", mockcrawl)

    crawler.start_crawler()
    assert crawler.sitemap == {"http://test.com": {"http://test.com/link"},
                               "http://test.com/link": {"http://test.com/link"}}
    assert crawler.assets == {"http://test.com": {"http://test.com/link", "http://test.com/resource"},
                              "http://test.com/link": {"http://test.com/link", "http://test.com/resource"}}


def test_crawler_non_html_link(crawler, monkeypatch, monkeypatch_requests_head_non_html):
    def mockcrawl(url):
        links = {"http://test.com/link"}
        resources = set()
        return links, resources

    monkeypatch.setattr(crawler, "crawl_url", mockcrawl)

    crawler.start_crawler()
    assert crawler.sitemap == {"http://test.com": set()}
    assert crawler.assets == {"http://test.com": {"http://test.com/link"}}


def test_crawler_no_content_type_link(crawler, monkeypatch, monkeypatch_requests_head_no_content_type):
    def mockcrawl(url):
        links = {"http://test.com/link"}
        resources = set()
        return links, resources

    monkeypatch.setattr(crawler, "crawl_url", mockcrawl)

    crawler.start_crawler()
    assert crawler.sitemap == {"http://test.com": {"http://test.com/link"},
                               "http://test.com/link": {"http://test.com/link"}}
    assert crawler.assets == {"http://test.com": {"http://test.com/link"},
                              "http://test.com/link": {"http://test.com/link"}}


def test_crawler_non_http_link(crawler, monkeypatch):
    def mockcrawl(url):
        links = {"mailto:mail@test.com"}
        resources = set()
        return links, resources

    monkeypatch.setattr(crawler, "crawl_url", mockcrawl)

    crawler.start_crawler()
    assert crawler.sitemap == {"http://test.com": set()}
    assert crawler.assets == {"http://test.com": set()}


def test_crawler_invalid_link(crawler, monkeypatch, monkeypatch_requests_head_invalid):
    def mockcrawl(url):
        links = {"http://test.com/link"}
        resources = set()
        return links, resources

    monkeypatch.setattr(crawler, "crawl_url", mockcrawl)

    crawler.start_crawler()
    assert crawler.sitemap == {"http://test.com": set()}
    assert crawler.assets == {"http://test.com": set()}


def test_crawler_matching_link_resource(crawler, monkeypatch, monkeypatch_requests_head):
    def mockcrawl(url):
        links = {"http://test.com/link"}
        resources = {"http://test.com/link"}
        return links, resources

    monkeypatch.setattr(crawler, "crawl_url", mockcrawl)

    crawler.start_crawler()
    assert crawler.sitemap == {"http://test.com": {"http://test.com/link"},
                               "http://test.com/link": {"http://test.com/link"}}
    assert crawler.assets == {"http://test.com": {"http://test.com/link"},
                              "http://test.com/link": {"http://test.com/link"}}
