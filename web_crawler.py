import argparse
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
    parser = argparse.ArgumentParser()
    parser.add_argument("domain", help="The domain to crawl (e.g. yoyowallet.com)")
    parser.add_argument("--workers", type=int, nargs="?", default=8, help="The number of workers to start (default = 8)")
    args = parser.parse_args()

    logger = multiprocessing.log_to_stderr()

    t0 = time.time()
    crawler = Crawler(args.domain)

    pool = Pool(args.workers, crawler.start_crawler)

    pool.close()
    pool.join()
    t1 = time.time()

    print_results(crawler.sitemap, crawler.assets)

    print "Total time: " + str(t1-t0)
