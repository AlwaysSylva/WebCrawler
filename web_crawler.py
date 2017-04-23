import multiprocessing
from multiprocessing import Pool

from crawler.crawler import Crawler


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
    import time
    logger = multiprocessing.log_to_stderr()

    t0 = time.time()
    crawler = Crawler("yoyowallet.com")

    pool = Pool(8, crawler.start_crawler)

    pool.close()
    pool.join()
    t1 = time.time()

    print_results(crawler.sitemap, crawler.assets)

    print "Total time: " + str(t1-t0)
