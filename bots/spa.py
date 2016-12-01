import os, inspect
from urllib.request import urlopen
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

MAX_PAGES_TO_SEARCH = 3

def parse_news(item):
    '''Parse news item
    return is a tuple(id, title, url)
    '''
    url = 'http://www.spa.gov.sa' + item['href']
    url_parsed = urlparse(url)
    qs = parse_qs(url_parsed[4])
    id = qs['newsid'][0]
    title = item.h2.contents[0]
    title = " ".join(title.split())
    item_parsed = (id, title, url)
    return item_parsed


def retrieve_news(person, last_id=-1):
    '''Retrieve news for person
    if last_id not definend it will return the max
    return list of news tuples up to MAX_PAGES_TO_SEARCH (page = 10 news)
    [(id, title, url)...]
    '''
    all_news = []
    found  = False
    page = 1
    while (page <= MAX_PAGES_TO_SEARCH and not found):
        url = ("http://www.spa.gov.sa/ajax/listnews.php?sticky={}&cat=0&cabine"
        "t=0&royal=0&lang=ar&pg={}".format(person, page))
        html = urlopen(url)
        soup = BeautifulSoup(html, "html.parser")
        news  =  soup.find_all("a", class_="aNewsTitle")
        for item in news:
            item_parsed = parse_news(item)
            if item_parsed[0] == str(last_id):
                found = True
                break
            all_news.append(item_parsed)
        page = page + 1
    return all_news


def arrival_news(person, last_id=-1):
    '''Retrive only arrival news for person
    if last_id not defiend it will return the max
    return list of arrival news tuples up to MAX_PAGES_TO_SEARCH (page = 10 news)
    [(id, title, url, location)...]
    '''
    arrival_news = []
    all_news = retrieve_news(person, last_id)
    for item in all_news:
        if 'يصل إلى' in item[1]:
            _list = list(item)
            _list.insert(3, (item[1].split('يصل إلى'))[1].split('قادماً من')[0])
            item = tuple(_list)
            arrival_news.append(item)
    return arrival_news


if __name__ == "__main__":
    # just for testing
    news = arrival_news(1)
    print(news)
