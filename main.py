import configparser
import bs4
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlparse, urlunparse, urljoin


def spider(target, exclude):
    parsed_target = urlparse(target)
    return spider_rec(dict(), target, parsed_target, exclude)


def spider_rec(page_links, current_href, base_parse, exclude):
    target_url = urlunparse(base_parse)
    parse_result = urlparse(urljoin(target_url, current_href))
    req = Request(urlunparse(parse_result))

    postfix = parse_result.path
    if parse_result.query:
        postfix += "?" + parse_result.query
    
    if len(postfix) == 0:
        postfix = "/"

    try:
        html_page = urlopen(req)
       
        if parse_result.hostname == base_parse.hostname:
            page_links[postfix] = []

            soup = bs4.BeautifulSoup(html_page, "lxml")

            for link in soup.findAll('a'):
                href = link.get('href')
                href = href.replace(" ", "%20")

                if "mailto:" not in href:
                    if not urlparse(href).hostname:
                        href_parse = urlparse(urljoin(target_url, href))
                        href = href_parse.path

                        if href_parse.query:
                            href += "?" + href_parse.query
                    
                    if href not in page_links[postfix]:
                        page_links[postfix].append(href)
                    
                    found = False
                    for key in page_links.keys() - [postfix]:
                        for link in page_links[key]:
                            if href == key or href == link:
                                found = True
                                break

                    if not found:
                        found = False
                        for d in exclude:
                            if d in href:
                                found = True
                                break

                        if found:
                            continue

                        spider_rec(page_links, href, base_parse, exclude)
    except HTTPError as e:
        if e.code == 400 or e.code in range(404, 500):
            if parse_result.hostname == base_parse.hostname:
                page_links[postfix] = e
            else:
                page_links[current_href] = e

    return page_links


def main():
    print("Reading conf...")

    config = configparser.ConfigParser()
    config.read('crawl.conf')
    config = config['Config']

    target = config['site']
    ignores = config['ignore'].split(', ')

    print("Crawling site...")
    pages = spider(target, ignores)

    print(f"Crawled {len(pages)} pages.")

    testedLinks = []
    for key in pages.keys():
        testedLinks += pages[key] + [key]
    testedLinks = list(set(testedLinks))
    print(f"Tested {len(testedLinks)} links.\n")

    count = 0
    for link in pages.keys():
        if type(pages[link]) == HTTPError:
            count += 1

            found = []
            for search_link in pages.keys():
                if type(pages[search_link]) != HTTPError:
                    for href in pages[search_link]:
                        if href == link:
                            found.append(search_link)

            print(''.join(['='] * 100))
            print(link, pages[link].status, pages[link].reason)
            print(''.join(['-'] * 100))
            print("Found in:")

            for href in found:
                print(href)

            print(''.join(['='] * 100), "\n")

    print("Done.")


main()
