from HTMLParser import HTMLParser
from urlparse import urljoin


class HTMLResourcesParser(HTMLParser):
    '''Extension of HTMLParser.HTMLParser which extracts links and resources from a provided html document
    
    Links are extracted from every <a href="*"> tag
    Resources are extracted from every <link href="*"> tag and tags with src="*" attribute
    
    '''
    def __init__(self, base_url):
        HTMLParser.__init__(self)
        self.links = set()
        self.resources = set()
        self.base_url = base_url

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    url = urljoin(self.base_url, value).strip('/')
                    self.links.add(url)
        if tag == 'link':
            for (key, value) in attrs:
                if key == 'href':
                    url = urljoin(self.base_url, value).strip('/')
                    self.resources.add(url)
        for (key, value) in attrs:
            if key == 'src':
                url = urljoin(self.base_url, value).strip('/')
                self.resources.add(url)

    def extract_links_and_assets(self, html):
        '''Parses the provided html document and returns links and resources extracted from it
    
        Links are extracted from every <a href="*"> tag
        Resources are extracted from every <link href="*"> tag and tags with src="*" attribute
        
        :param html: The html document to parse
        :return: Returns a tuple (links, resources) of links and resources extracted
        '''
        self.links = set()
        self.resources = set()
        self.feed(html)
        return self.links, self.resources