import bs4
from urllib.request import Request, urlopen


def spider(prefix, domain, exclude):
    return spider_rec(dict(), prefix, domain, "/", exclude)


def spider_rec(page_links, prefix, domain, postfix, exclude):
    req = Request(prefix + domain + postfix)
    html_page = urlopen(req)

    print(html_page.status)
    page_links[postfix] = []

    soup = bs4.BeautifulSoup(html_page, "lxml")

    for link in soup.findAll('a'):
        href = link.get('href')
        if "mailto:" not in href and (domain in href or href[0] == '/'):
            page_links[postfix].append(href)

            if href not in page_links.keys():
                found = False
                for d in exclude:
                    if d in href:
                        found = True
                        break

                if found:
                    continue

                href = href.replace(" ", "%20")
                if domain in href:
                    spider_rec(page_links, "", "", href, exclude)
                else:
                    spider_rec(page_links, prefix, domain, href, exclude)

    return page_links


def main():
    print("Reading conf...")

    conf = []
    with open('crawl.conf', 'r') as file:
        for line in file.readlines():
            line = line.replace("\n", "")
            line = line.replace("\r", "")
            conf.append(line)

    domain = conf[1]
    prefix = conf[3]
    ignores = conf[5:]

    print("Crawling site...")
    links = spider(prefix, domain, ignores)


main()
