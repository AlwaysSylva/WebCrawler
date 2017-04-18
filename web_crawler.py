import multiprocessing
from Queue import Empty
from multiprocessing import Pool, Manager


def get_html(url, q, urls, assets):
    response = "blah"
    q.put((extract_links, response))
    q.put((extract_assets, response))
    return


def extract_links(html, q, urls, assets):
    link = "http://yoyowallet.com/team.html"
    if link not in urls:
        urls.append(link)
        q.put((get_html, link))
        return
    return


def extract_assets(html, q, urls, assets):
    asset = "http://yoyowallet.com/asset"
    if asset not in assets:
        assets.append(asset)
    return


def process_job(q, urls, assets):
    while True:
        try:
            job = q.get(timeout=1)
        except Empty:
            break
        job[0](job[1], q, urls, assets)
    return


if __name__ == '__main__':
    logger = multiprocessing.log_to_stderr()

    manager = Manager()
    urls = manager.list(["http://yoyowallet.com"])
    assets = manager.list([])
    q = manager.Queue()
    q.put((get_html, "http://yoyowallet.com"))

    pool = Pool(4, process_job, (q, urls, assets))

    pool.close()
    pool.join()
    print urls
    print assets
