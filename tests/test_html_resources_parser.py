import pytest

from crawler.html_resources_parser import HTMLResourcesParser


@pytest.fixture
def base_url():
    return "http://test.com"


@pytest.fixture
def parser(base_url):
    return HTMLResourcesParser(base_url)


def test_extract_none(parser):
    html = "<none>"
    (links, resources) = parser.extract_links_and_assets(html)
    assert links == set()
    assert resources == set()


def test_extract_absolute_link(parser):
    link_url = "http://www.absolute.com"
    html = "<a href={}/>".format(link_url)
    (links, resources) = parser.extract_links_and_assets(html)
    assert links == {link_url}


def test_extract_relative_link(base_url, parser):
    link_url = "/relative_url"
    html = "<a href={}/>".format(link_url)
    (links, resources) = parser.extract_links_and_assets(html)
    assert links == {base_url + link_url}


def test_extract_absolute_link_resource(parser):
    resource_url = "http://www.absolute.com"
    html = "<link href={}/>".format(resource_url)
    (links, resources) = parser.extract_links_and_assets(html)
    assert resources == {resource_url}


def test_extract_relative_link_resource(base_url, parser):
    resource_url = "/relative_url"
    html = "<link href={}/>".format(resource_url)
    (links, resources) = parser.extract_links_and_assets(html)
    assert resources == {base_url + resource_url}


def test_extract_absolute_src_resource(parser):
    resource_url = "http://www.absolute.com"
    html = "<anytag src={}/>".format(resource_url)
    (links, resources) = parser.extract_links_and_assets(html)
    assert resources == {resource_url}


def test_extract_relative_src_resource(base_url, parser):
    resource_url = "/relative_url"
    html = "<anytag src={}/>".format(resource_url)
    (links, resources) = parser.extract_links_and_assets(html)
    assert resources == {base_url + resource_url}
