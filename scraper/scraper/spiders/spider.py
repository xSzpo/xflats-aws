import scrapy
import codecs
import json
import logging
import re
import zlib
import base64
import unidecode
import numpy as np
from scrapy.exceptions import DropItem
from dateutil.parser import parse
from helpers.base import Scraper
from helpers.base import Geodata

logger = logging.getLogger(__name__)


class SpiderFlatOtodom(scrapy.Spider):

    def __init__(self):
        super().__init__()
        self.pageCounter = 1
        self.mongo_connection = None

    name = "otodom"

    xpath_json = None

    with codecs.open("./scraper/spiders/xhpats.json", "r") as file:
        xpath_json = json.load(file)

    start_urls = xpath_json['otodom']['start_urls']
    list_page_start_xpath = xpath_json['otodom']['list_page_start_xpath']
    list_page_iter_xpaths = xpath_json['otodom']['list_page_iter_xpaths']
    next_page_css = xpath_json['otodom']['next_page_css']
    article_page_iter_xpaths = xpath_json['otodom']['article_page_iter_xpaths']

    allowed_domains = ["www.otodom.pl"]

    def parse(self, response):
        for i, offer in enumerate(response.xpath(self.list_page_start_xpath)):
            url = offer.xpath(self.list_page_iter_xpaths['url']).get()
            if url:
                url = 'https://www.otodom.pl'+url
                yield scrapy.Request(url, callback=self.parse_dir_contents)

        # after you crawl each offer in current page go to the next page
        reg = r"/?page=(\d+)"
        match = re.search(reg, response.url)
        if match:
            page_num = int(match.group(1))
            next_page = response.url+f'?page={page_num+1}'
        else:
            next_page = response.url+'?page=2'

        if next_page is not None and self.pageCounter < \
                self.settings['CRAWL_LIST_PAGES']:
            if next_page is not None and self.pageCounter >= 1:
                logger.info("OTODOM: next page, iter {}, url: {}".format(
                    self.pageCounter, next_page))
            self.pageCounter += 1
            yield response.follow(next_page, callback=self.parse)

    def parse_dir_contents(self, response):

        tmp = {}

        for key in self.article_page_iter_xpaths:
            tmp[key] = response.xpath(self.article_page_iter_xpaths[key]).get()

        if tmp['floor']:
            tmp['floor'] = tmp['floor'] if '/' not in tmp['floor'] else tmp['floor'].split('/')[0]
            tmp['number_of_floors'] = None if '/' not in tmp['number_of_floors'] else tmp['number_of_floors'].split('/')[-1]

        #tmp['additional_info'] = " | ".join(
        #    response.xpath(self.article_page_iter_xpaths['additional_info']).getall()
        #    )
        _tmp1 = response.xpath(self.article_page_iter_xpaths['additional_info']).getall()
        _tmp1 = [i for i in _tmp1 if '.css' not in i]

        _tmp2 = response.xpath(self.article_page_iter_xpaths['additional_info2']).getall()
        _tmp2 = [i for i in _tmp2 if '.css' not in i]

        if len(_tmp1) > 0:
            tmp['additional_info'] = "|".join(_tmp1)
        else:
            tmp['additional_info'] = ""

        if len(_tmp2) > 0:
            tmp['additional_info2'] = "|".join(_tmp2)
        else:
            tmp['additional_info'] = ""
        
        tmp['additional_info'] = tmp['additional_info']+"|"+tmp['additional_info2']

        tmp.pop('additional_info2')

        tmp['description'] = "\n".join(response.xpath(
            self.article_page_iter_xpaths['description']).getall())

        tmp['geo_coordinates'] = Geodata.get_geodata_otodom(response.body)

        regex = r'"dateCreated":"(20\d\d-[01]\d-[0-3]\d [0-3]\d:[0-5]\d:' + \
                r'[0-5]\d)","dateModified":"(20\d\d-[01]\d-[0-3]\d ' + \
                r'[0-3]\d:[0-5]\d:[0-5]\d)"'

        tmp['date_created'] = Scraper.searchregex(response.body.decode(),
                                                  regex, group=1, func=parse)
        tmp['date_modified'] = Scraper.searchregex(response.body.decode(),
                                                   regex, group=2, func=parse)

        tmp['tracking_id'] = Scraper.searchregex(response.body.decode(),
                                                  "ad.:{.id.:(\d+)", group=1)
        tmp['url'] = response.url
        tmp['producer_name'] = self.name
        tmp['main_url'] = self.start_urls[0]
        # zlib.decompress(base64.b64decode(x))
        if self.settings['SAVE_BODY']:
            tmp['body'] = base64.b64encode(zlib.compress(response.body)).decode()
        else:
            tmp.pop('body', None)
        
        #tmp['offeror'] = offeror
        #_tmp = tmp.copy()
        #_tmp.pop('body')
        #_tmp.pop('description')
        #logger.info(_tmp['offeror'])

        yield tmp


class SpiderFlatOlx(scrapy.Spider):

    def __init__(self):
        super().__init__()
        self.pageCounter = 1
        self.mongo_connection = None

    name = "olx"

    xpath_json = None

    with codecs.open("./scraper/spiders/xhpats.json", "r") as file:
        xpath_json = json.load(file)

    start_urls = xpath_json['olx']['start_urls']
    list_page_url = xpath_json['olx']['url']
    next_page_css = xpath_json['olx']['next_page_css']
    article_page_iter_xpaths = xpath_json['olx']['article_page_iter_xpaths']

    allowed_domains = ["www.olx.pl"]

    def parse(self, response):
        for i, url in enumerate(response.xpath(self.list_page_url).getall()):
            yield scrapy.Request(url, callback=self.parse_dir_contents)

        # after you crawl each offer in current page go to the next page
        next_page = response.css(self.next_page_css).get()

        if next_page is not None and self.pageCounter < \
                self.settings['CRAWL_LIST_PAGES']:
            if next_page is not None and self.pageCounter >= 1:
                logger.info("OLX: next page, iter {}, url: {}".format(
                    self.pageCounter, next_page))
            self.pageCounter += 1
            yield response.follow(next_page, callback=self.parse)

    def parse_dir_contents(self, response):

        tmp = {}

        for key in self.article_page_iter_xpaths:
            tmp[key] = response.xpath(self.article_page_iter_xpaths[key]).get()

        tmp['additional_info'] = "|".join(response.xpath(
            self.article_page_iter_xpaths['additional_info']).getall()).strip()
        tmp['description'] = "\n".join(response.xpath(
            self.article_page_iter_xpaths['description']).getall())
        tmp['geo_coordinates'] = Geodata.get_geodata_olx(response.body)

        tmp['date_created'] = Scraper.searchregex(
            response.body.decode("utf-8"), r'createdTime\W+(\d{4}-\d{2}-\d{2})', group=1)

        tmp['date_modified'] = Scraper.searchregex(
            response.body.decode("utf-8"), r'lastRefreshTime\W+(\d{4}-\d{2}-\d{2})', group=1)

        tmp['url'] = response.url
        tmp['producer_name'] = self.name
        tmp['main_url'] = self.start_urls[0]

        tmp['number_of_floors'] = Scraper.searchregex(
            tmp['description'].lower(), r'\d+\W+pi.tr(?:ow|a)', group=0)

        reg = (r"(oddan\w+|inwestyc\w+|odbi.r\w+|rok\s+budow\w+|blok\w+|" +
               r"dom\w+|kamienic\w+|budyn\w+)[\w\S ]*(1[89]\d\d|20\d\d)")

        tmp['year_of_building'] = Scraper.searchregex(
            tmp['description'].lower(), reg, group=2)

        tmp['location'] = Scraper.searchregex(unidecode.unidecode(response.body.decode("utf-8")), r"pathName\W+([A-z,\s]+)", group=1).replace('\\','')

        #zlib.decompress(base64.b64decode(x))
        if self.settings['SAVE_BODY']:
            tmp['body'] = base64.b64encode(zlib.compress(response.body)).decode()
        else:
            tmp.pop('body', None)

        tmp['building_material'] = None

        yield tmp


class SpiderFlatGratka(scrapy.Spider):

    def __init__(self):
        super().__init__()
        self.pageCounter = 1
        self.mongo_connection = None

    name = "gratka"

    xpath_json = None

    with codecs.open("./scraper/spiders/xhpats.json", "r") as file:
        xpath_json = json.load(file)

    start_urls = xpath_json['gratka']['start_urls']
    list_page_url = xpath_json['gratka']['url']
    next_page = xpath_json['gratka']['next_page']
    list_date_modified = xpath_json['gratka']['main_page_date_modified']
    article_page_iter_xpaths = xpath_json['gratka']['article_page_iter_xpaths']

    allowed_domains = ["gratka.pl"]

    def parse(self, response):

        urls = response.xpath(self.list_page_url).getall()

        for url in urls:

            yield scrapy.Request(url, callback=self.parse_dir_contents)

        # after you crawl each offer in current page go to the next page
        next_page = response.xpath(self.next_page).get()

        if next_page is not None and self.pageCounter < \
                self.settings['CRAWL_LIST_PAGES']:
            if next_page is not None and self.pageCounter >= 1:
                logger.info("GRATKA: next page, iter {}, url: {}".format(
                    self.pageCounter, next_page))
            self.pageCounter += 1
            yield response.follow(next_page, callback=self.parse)

    def parse_dir_contents(self, response):

        tmp = {}

        for key in self.article_page_iter_xpaths:
            tmp[key] = response.xpath(self.article_page_iter_xpaths[key]).get()

        tmp['tracking_id'] = re.findall(r"\d+", response.url.split("/")[-1])[0]
        tmp['location'] = ", ".join(response.xpath(
            self.article_page_iter_xpaths['location']).getall())
        tmp['description'] = "\n".join(response.xpath(
            self.article_page_iter_xpaths['description']).getall())
        tmp['additional_info'] = re.sub(r"\W+", " ", " ".join(response.xpath(
            self.article_page_iter_xpaths['additional_info']).getall()).strip())
        tmp['geo_coordinates'] = Geodata.get_geodata_gratka(response.body)
        tmp['market'] = Scraper.searchregex(
            response.body.decode(), r"('rynek', .(\w+).)", group=2)
        tmp['offeror'] = None

        tmp['date_created'] = None
        tmp['date_modified'] = None
        tmp['date_modified'] = None

        tmp['url'] = response.url
        tmp['producer_name'] = self.name
        tmp['main_url'] = self.start_urls[0]

        #zlib.decompress(base64.b64decode(x))
        if self.settings['SAVE_BODY']:
            tmp['body'] = base64.b64encode(zlib.compress(response.body)).decode()
        else:
            tmp.pop('body', None)

        yield tmp


class SpiderFlatMorizon(scrapy.Spider):

    def __init__(self):
        super().__init__()
        self.pageCounter = 1
        self.mongo_connection = None

    name = "morizon"

    xpath_json = None

    with codecs.open("./scraper/spiders/xhpats.json", "r") as file:
        xpath_json = json.load(file)

    start_urls = xpath_json['morizon']['start_urls']
    list_page_url = xpath_json['morizon']['url']
    next_page = xpath_json['morizon']['next_page']
    article_page_iter_xpaths = xpath_json['morizon']['article_page_iter_xpaths']

    allowed_domains = ["www.morizon.pl"]

    def parse(self, response):

        for i, url in enumerate(response.xpath(self.list_page_url).getall()):
            yield scrapy.Request(url, callback=self.parse_dir_contents)

        # after you crawl each offer in current page go to the next page
        next_page = response.xpath(self.next_page).get()

        if next_page is not None and self.pageCounter < \
                self.settings['CRAWL_LIST_PAGES']:
            if next_page is not None and self.pageCounter >= 1:
                logger.info("MORIZON: next page, iter {}, url: {}".format(
                    self.pageCounter, next_page))
            self.pageCounter += 1
            yield response.follow(next_page, callback=self.parse)

    def parse_dir_contents(self, response):

        tmp = {}

        for key in self.article_page_iter_xpaths:
            tmp[key] = response.xpath(self.article_page_iter_xpaths[key]).get()

        tmp['name'] = " ".join(response.xpath(
            self.article_page_iter_xpaths['name']).getall())
        tmp['location'] = " ".join(response.xpath(
            self.article_page_iter_xpaths['location']).getall())

        tmp['geo_coordinates'] = {
            "latitude": tmp['data_lat'], "longitude": tmp['data_lon']}
        tmp['tracking_id'] = re.findall(r"\d+", response.url.split("-")[-1])[0]
        tmp['description'] = "\n".join(response.xpath(
            self.article_page_iter_xpaths['description']).getall())
        tmp['url'] = response.url
        tmp['producer_name'] = self.name
        tmp['main_url'] = self.start_urls[0]

        tmp['offeror'] = Scraper.searchregex(response.body.decode(),
                                             r"oferent=(\w+);", group=1)
        tmp['floor'] = Scraper.searchregex(tmp['floor'], r"(\d+).+", group=1)

        tmp['date_created'] = Scraper.searchregex(
            tmp['date_created'], r"\d\d-[01]\d-20\d\d", group=0)
        tmp['date_created'] = parse(tmp['date_created'], dayfirst=True)

        tmp['date_modified'] = Scraper.\
            get_createdate_polish_months(tmp['date_modified'])

        #zlib.decompress(base64.b64decode(x))
        if self.settings['SAVE_BODY']:
            tmp['body'] = base64.b64encode(zlib.compress(response.body)).decode()
        else:
            tmp.pop('body', None)

        yield tmp


class Spiderprzedajemy(scrapy.Spider):

    def __init__(self):
        super().__init__()
        self.pageCounter = 1
        self.mongo_connection = None

    name = "plot_sprzedajemy"

    xpath_json = None

    with codecs.open("./scraper/spiders/xhpats.json", "r") as file:
        xpath_json = json.load(file)

    start_urls = xpath_json['sprzedajemy_dzialka']['start_urls']
    list_page_url = xpath_json['sprzedajemy_dzialka']['url']
    next_page_css = xpath_json['sprzedajemy_dzialka']['next_page_css']
    list_date_modified = xpath_json['sprzedajemy_dzialka']['main_page_date_modified']
    article_page_iter_xpaths = xpath_json['sprzedajemy_dzialka']['article_page_iter_xpaths']

    allowed_domains = ["sprzedajemy.pl"]

    def parse(self, response):

        urls = response.xpath(self.list_page_url).getall()
        dates_upd = response.xpath(self.list_date_modified).getall()

        #for i, url in enumerate(urls):
        #    yield scrapy.Request(response.urljoin(url), callback=self.parse_dir_contents)

        for i, url in enumerate([i for i in zip(urls, dates_upd)]):
            yield scrapy.Request(response.urljoin(url[0]),
                                 callback=self.parse_dir_contents,
                                 cb_kwargs=dict(date_modified=url[1]))

        # after you crawl each offer in current page go to the next page
        next_page = response.css(self.next_page_css).get()

        if next_page is not None and self.pageCounter < \
                self.settings['CRAWL_LIST_PAGES']:
            if next_page is not None and self.pageCounter >= 1:
                logger.info("SPRZEDAJEMY_DZIALKA: next page, iter {}, url: {}".format(
                    self.pageCounter, next_page))
            self.pageCounter += 1
            yield response.follow(next_page, callback=self.parse)

    def parse_dir_contents(self, response, date_modified):

        tmp = {}

        for key in self.article_page_iter_xpaths:
            tmp[key] = response.xpath(self.article_page_iter_xpaths[key]).get()

        tmp['location'] = " ".join(response.xpath(
            self.article_page_iter_xpaths['location']).getall())

        tmp['description'] = "\n".join(response.xpath(
            self.article_page_iter_xpaths['description']).getall())

        tmp['additional_info'] = re.sub(r"\W+", " ", " ".join(response.xpath(
            self.article_page_iter_xpaths['additional_info']).
            getall()).strip())

        tmp['additional_info'] += " " + re.sub(r"\W+", " ", " ".join(
            response.xpath(self.article_page_iter_xpaths['additional_info2']).
            getall()).strip())

        tmp['geo_coordinates'] = {
            "latitude": json.loads(
                tmp['geo-coordinates'].replace("'", '"'))['lat'],
            "longitude": json.loads(
                tmp['geo-coordinates'].replace("'", '"'))['lng'],}

        tmp['url'] = response.url
        tmp['producer_name'] = self.name
        tmp['main_url'] = self.start_urls[0]

        tmp['date_created'] = None
        tmp['date_modified'] = parse(date_modified)

        #zlib.decompress(base64.b64decode(x))
        if self.settings['SAVE_BODY']:
            tmp['body'] = base64.b64encode(zlib.compress(response.body)).decode()
        else:
            tmp.pop('body', None)

        yield tmp


class SpiderPlotGumtree(scrapy.Spider):

    def __init__(self):
        super().__init__()
        self.pageCounter = 1
        self.mongo_connection = None

    name = "plot_gumtree"

    xpath_json = None

    with codecs.open("./scraper/spiders/xhpats.json", "r") as file:
        xpath_json = json.load(file)

    start_urls = xpath_json['gumtree_dzialka']['start_urls']
    list_page_url = xpath_json['gumtree_dzialka']['url']
    next_page = xpath_json['gumtree_dzialka']['next_page']
    article_page_iter_xpaths = xpath_json['gumtree_dzialka']['article_page_iter_xpaths']

    allowed_domains = ["gumtree.pl"]

    def parse(self, response):

        for i, url in enumerate(response.xpath(self.list_page_url).getall()):
            yield scrapy.Request(response.urljoin(url), callback=self.parse_dir_contents)

        # after you crawl each offer in current page go to the next page
        next_page = response.xpath(self.next_page).get()

        if next_page is not None and self.pageCounter < \
                self.settings['CRAWL_LIST_PAGES']:
            if next_page is not None and self.pageCounter >= 1:
                logger.info("SPRZEDAJEMY_DZIALKA: next page, iter {}, url: {}".format(
                    self.pageCounter, next_page))
            self.pageCounter += 1
            yield response.follow(next_page, callback=self.parse)

    def parse_dir_contents(self, response):

        tmp = {}

        for key in self.article_page_iter_xpaths:
            tmp[key] = response.xpath(self.article_page_iter_xpaths[key]).get()

        tmp['location'] = " ".join(response.xpath(
            self.article_page_iter_xpaths['location']).getall())

        tmp['description'] = "\n".join(response.xpath(
            self.article_page_iter_xpaths['description']).getall())

        tmp['price'] = tmp['price'].encode('ascii', 'ignore').decode()

        tmp['additional_info'] = None
        tmp['price_m2'] = None

        tmp['geo_coordinates'] = {
            "latitude": tmp['geo-coordinates'].split(',')[0],
            "longitude": tmp['geo-coordinates'].split(',')[1]}

        size0 = Scraper.searchregex(tmp['name'], r"(\d+ ?\d{3,})m2", group=1)
        size1 = Scraper.searchregex(tmp['name']+' '+tmp['description'], r"powierz\w+\W+(\d+ ?\d{3,})", group=1)
        size2 = Scraper.searchregex(tmp['name']+' '+tmp['description'], r"(\d+ ?\d{3,})m2", group=1)
        tmp['size'] = size0 or size1 or size2

        tmp['url'] = response.url
        tmp['producer_name'] = self.name
        tmp['main_url'] = self.start_urls[0]

        tmp['date_created'] = parse(tmp['date_created'], dayfirst=True)
        tmp['date_modified'] = None

        #zlib.decompress(base64.b64decode(x))
        if self.settings['SAVE_BODY']:
            tmp['body'] = base64.b64encode(zlib.compress(response.body)).decode()
        else:
            tmp.pop('body', None)

        yield tmp


class SpiderPlotOlx(scrapy.Spider):

    def __init__(self):
        super().__init__()
        self.pageCounter = 1
        self.mongo_connection = None

    name = "plot_olx"

    xpath_json = None

    with codecs.open("./scraper/spiders/xhpats.json", "r") as file:
        xpath_json = json.load(file)

    start_urls = xpath_json['olx_dzialka']['start_urls']
    list_page_url = xpath_json['olx_dzialka']['url']
    next_page_css = xpath_json['olx_dzialka']['next_page_css']
    article_page_iter_xpaths = xpath_json['olx_dzialka']['article_page_iter_xpaths']

    allowed_domains = ["www.olx.pl"]

    def parse(self, response):
        for i, url in enumerate(response.xpath(self.list_page_url).getall()):
            yield scrapy.Request(url, callback=self.parse_dir_contents)

        # after you crawl each offer in current page go to the next page
        next_page = response.css(self.next_page_css).get()

        if next_page is not None and self.pageCounter < \
                self.settings['CRAWL_LIST_PAGES']:
            if next_page is not None and self.pageCounter >= 1:
                logger.info("OLX: next page, iter {}, url: {}".format(
                    self.pageCounter, next_page))
            self.pageCounter += 1
            yield response.follow(next_page, callback=self.parse)

    def parse_dir_contents(self, response):

        tmp = {}

        for key in self.article_page_iter_xpaths:
            tmp[key] = response.xpath(self.article_page_iter_xpaths[key]).get()

        tmp['additional_info'] = re.sub(r"\W+", " ", " ".join(response.xpath(
            self.article_page_iter_xpaths['additional_info']).getall()).strip())
        tmp['description'] = "\n".join(response.xpath(
            self.article_page_iter_xpaths['description']).getall())
        tmp['geo_coordinates'] = Geodata.get_geodata_olx(response.body)
        tmp['date_created'] = Scraper.\
            get_createdate_polish_months(tmp['date_created'])
        tmp['date_modified'] = None
        tmp['url'] = response.url
        tmp['producer_name'] = self.name
        tmp['main_url'] = self.start_urls[0]

        #zlib.decompress(base64.b64decode(x))
        if self.settings['SAVE_BODY']:
            tmp['body'] = base64.b64encode(zlib.compress(response.body)).decode()
        else:
            tmp.pop('body', None)

        yield tmp


class SpiderPlotGratka(scrapy.Spider):

    def __init__(self):
        super().__init__()
        self.pageCounter = 1
        self.mongo_connection = None

    name = "plot_gratka"

    xpath_json = None

    with codecs.open("./scraper/spiders/xhpats.json", "r") as file:
        xpath_json = json.load(file)

    start_urls = xpath_json['gratka_dzialka']['start_urls']
    list_page_url = xpath_json['gratka_dzialka']['url']
    next_page = xpath_json['gratka_dzialka']['next_page']
    list_date_modified = xpath_json['gratka_dzialka']['main_page_date_modified']
    article_page_iter_xpaths = xpath_json['gratka_dzialka']['article_page_iter_xpaths']

    allowed_domains = ["gratka.pl"]

    def parse(self, response):

        urls = response.xpath(self.list_page_url).getall()
        dates_upd = response.xpath(self.list_date_modified).getall()

        for i, url in enumerate([i for i in zip(urls, dates_upd)]):

            yield scrapy.Request(url[0], callback=self.parse_dir_contents,
                                 cb_kwargs=dict(date_modified=url[1]))

        # after you crawl each offer in current page go to the next page
        next_page = response.xpath(self.next_page).get()

        if next_page is not None and self.pageCounter < \
                self.settings['CRAWL_LIST_PAGES']:
            if next_page is not None and self.pageCounter >= 1:
                logger.info("GRATKA: next page, iter {}, url: {}".format(
                    self.pageCounter, next_page))
            self.pageCounter += 1
            yield response.follow(next_page, callback=self.parse)

    def parse_dir_contents(self, response, date_modified):

        tmp = {}

        for key in self.article_page_iter_xpaths:
            tmp[key] = response.xpath(self.article_page_iter_xpaths[key]).get()

        tmp['tracking_id'] = re.findall(r"\d+", response.url.split("/")[-1])[0]
        tmp['location'] = ", ".join(response.xpath(
            self.article_page_iter_xpaths['location']).getall())
        tmp['description'] = "\n".join(response.xpath(
            self.article_page_iter_xpaths['description']).getall())
        tmp['additional_info'] = re.sub(r"\W+", " ", " ".join(response.xpath(
            self.article_page_iter_xpaths['additional_info']).getall()).strip())
        tmp['geo_coordinates'] = Geodata.get_geodata_gratka(response.body)

        tmp['offeror'] = None

        tmp['date_created'] = None
        tmp['date_modified'] = Scraper.searchregex(
            date_modified, r"\d\d.[01]\d.20\d\d", group=0)
        tmp['date_modified'] = parse(tmp['date_modified'], dayfirst=True)

        tmp['url'] = response.url
        tmp['producer_name'] = self.name
        tmp['main_url'] = self.start_urls[0]

        #zlib.decompress(base64.b64decode(x))
        if self.settings['SAVE_BODY']:
            tmp['body'] = base64.b64encode(zlib.compress(response.body)).decode()
        else:
            tmp.pop('body', None)

        yield tmp


class SpiderPlotOtodom(scrapy.Spider):

    def __init__(self):
        super().__init__()
        self.pageCounter = 1
        self.mongo_connection = None

    name = "plot_otodom"

    xpath_json = None

    with codecs.open("./scraper/spiders/xhpats.json", "r") as file:
        xpath_json = json.load(file)

    start_urls = xpath_json['otodom_dziaka']['start_urls']
    list_page_start_xpath = xpath_json['otodom_dziaka']['list_page_start_xpath']
    list_page_iter_xpaths = xpath_json['otodom_dziaka']['list_page_iter_xpaths']
    next_page_css = xpath_json['otodom_dziaka']['next_page_css']
    article_page_iter_xpaths = xpath_json['otodom_dziaka']['article_page_iter_xpaths']

    allowed_domains = ["www.otodom.pl"]

    def parse(self, response):
        for i, offer in enumerate(response.xpath(self.list_page_start_xpath)):
            url = offer.xpath(self.list_page_iter_xpaths['url']).get()
            offeror = offer.xpath(self.list_page_iter_xpaths['offeror']).get().strip()
            yield scrapy.Request(url, callback=self.parse_dir_contents,
                                    cb_kwargs=dict(offeror=offeror))

        # after you crawl each offer in current page go to the next page
        next_page = response.css(self.next_page_css).get()

        if next_page is not None and self.pageCounter < \
                self.settings['CRAWL_LIST_PAGES']:
            if next_page is not None and self.pageCounter >= 1:
                logger.info("OTODOM: next page, iter {}, url: {}".format(
                    self.pageCounter, next_page))
            self.pageCounter += 1
            yield response.follow(next_page, callback=self.parse)

    def parse_dir_contents(self, response, offeror):

        tmp = {}

        for key in self.article_page_iter_xpaths:
            tmp[key] = response.xpath(self.article_page_iter_xpaths[key]).get()

        tmp['additional_info'] = " ".join(response.xpath(
            self.article_page_iter_xpaths['additional_info']).getall())
        tmp['description'] = "\n".join(response.xpath(
            self.article_page_iter_xpaths['description']).getall())
        tmp['geo_coordinates'] = Geodata.get_geodata_otodom(response.body)

        regex = r'"dateCreated":"(20\d\d-[01]\d-[0-3]\d [0-3]\d:[0-5]\d:' + \
                r'[0-5]\d)","dateModified":"(20\d\d-[01]\d-[0-3]\d ' + \
                r'[0-3]\d:[0-5]\d:[0-5]\d)"'

        tmp['date_created'] = Scraper.searchregex(response.body.decode(),
                                                  regex, group=1, func=parse)
        tmp['date_modified'] = Scraper.searchregex(response.body.decode(),
                                                   regex, group=2, func=parse)
        tmp['url'] = response.url
        tmp['producer_name'] = self.name
        tmp['main_url'] = self.start_urls[0]
        tmp['offeror'] = offeror
        tmp['tracking_id'] = Scraper.searchregex(response.body.decode(),
                                                  "ad.:{.id.:(\d+)", group=1)

        # zlib.decompress(base64.b64decode(x))
        if self.settings['SAVE_BODY']:
            tmp['body'] = base64.b64encode(zlib.compress(response.body)).decode()
        else:
            tmp.pop('body', None)

        yield tmp