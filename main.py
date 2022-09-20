import http
import bs4
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlparse, urlunparse, urljoin
import re


def spider(target, exclude):
    parsed_target = urlparse(target)
    return spider_rec(dict(), target, parsed_target, exclude)


def spider_rec(page_links, current_href, base_parse, exclude):
    target_url = urlunparse(base_parse)
    parse_result = urlparse(urljoin(target_url, current_href))
    req = Request(urlunparse(parse_result))
    postfix = parse_result.path
    
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
                
                if not urlparse(href).hostname:
                    href = urlparse(urljoin(target_url, href)).path         
                
                if "mailto:" not in href:
                    page_links[postfix].append(href)

                    if href not in page_links.keys():
                        found = False
                        for d in exclude:
                            if d in href:
                                found = True
                                break

                        if found:
                            continue

                        spider_rec(page_links, href, base_parse, exclude)
    except HTTPError as e:
        page_links[postfix] = e

    return page_links


def main():
    print("Reading conf...")

    conf = []
    with open('crawl.conf', 'r') as file:
        for line in file.readlines():
            line = line.replace("\n", "")
            line = line.replace("\r", "")
            conf.append(line)

    target = conf[1]
    ignores = conf[3:]

    print("Crawling site...")
    pages = spider(target, ignores)

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
