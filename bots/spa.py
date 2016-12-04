from urllib.request import urlopen
from urllib.parse import urlparse, parse_qs
from socket import error as SocketError
import errno
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


def retrieve_news(person=0, royal=0, cabinet=0,  last_id=-1):
    '''Retrieve news for person or royal
    person 1= king, 2= crown prince and 3= deputy crown prince
    if royal is = 1 news will be retriveved
    if last_id not definend it will return the max
    return list of news tuples up to MAX_PAGES_TO_SEARCH (page = 10 news)
    [(id, title, url)...]
    '''
    all_news = []
    found  = False
    page = 1
    while (page <= MAX_PAGES_TO_SEARCH and not found):
        url = ("http://www.spa.gov.sa/ajax/listnews.php?sticky={}&cat=0&cabine"
        "t={}&royal={}&lang=ar&pg={}".format(person, cabinet, royal,  page))
        try:
            html = urlopen(url)
            soup = BeautifulSoup(html, "html.parser")
            news  =  soup.find_all("a", class_="aNewsTitle")
            for item in news:
                item_parsed = parse_news(item)
                if item_parsed[0] <= str(last_id):
                    found = True
                    break
                all_news.append(item_parsed)
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise
            pass
        page = page + 1
    return all_news


def retrieve_detail(item):
    '''Retrive detaill for news item
    return is tuple (id, title, url, text)
    '''
    url = item[2]
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    detail = soup.find(class_='divNewsDetailsText')
    detail = detail.get_text()
    _list  = list(item)
    _list.insert(3, detail)
    item = tuple(_list)
    return item


def royal_order(last_id=-1):
    '''Retrive royal orders
    if last_id not defiend it will return the max
    return list of royal orders tuples up to MAX_PAGES_TO_SEARCH (page=10)
    [(id, title, url, text)...]
    '''
    orders = []
    _news = retrieve_news(royal=1, last_id=last_id)
    for item in _news:
        _detail = retrieve_detail(item)
        orders.append(_detail)
    return orders


def cabinet_decision(last_id=-1):
    '''Retrive cabinet decisions
    if last_id not defiend it will return the max
    return list of cabinet decisions tuples up to MAX_PAGES_TO_SEARCH (page=10)
    [(id, title, url, text)...]
    '''
    decisions = []
    _news = retrieve_news(cabinet=1, last_id=last_id)
    for item in _news:
        _detail = retrieve_detail(item)
        decisions.append(_detail)
    return decisions


def arrival_news(person, last_id=-1):
    '''Retrive only arrival news for person
    if last_id not defiend it will return the max
    return list of arrival news tuples up to MAX_PAGES_TO_SEARCH (page = 10 news)
    [(id, title, url, location)...]
    '''
    arrival_news = []
    all_news = retrieve_news(person=person, last_id= last_id)
    for item in all_news:
        if 'يصل إلى' in item[1]:
            _list = list(item)
            _list.insert(3, (item[1].split('يصل إلى'))[1].split('قادماً من')[0])
            item = tuple(_list)
            arrival_news.append(item)
    return arrival_news


def leave_news(person, last_id=-1):
    '''Retrive only leave news for person
    if last_id not defiend it will return the max
    return list of leave news tuples up to MAX_PAGES_TO_SEARCH (page = 10 news)
    [(id, title, url, locationFromTo)...]
    '''
    leave_news = []
    all_news = retrieve_news(person=person, last_id= last_id)
    for item in all_news:
        if 'يغادر' in item[1]:
            _list = list(item)
            _list.insert(3, item[1].split('يغادر')[1])
            item = tuple(_list)
            leave_news.append(item)
    return leave_news


if __name__ == "__main__":
    # just for testing
    news = cabinet_decision()
    print(news)
