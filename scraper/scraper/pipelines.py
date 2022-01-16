# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# utc epoch to time - time.gmtime(0)

import logging
import sys
import json
import re
import codecs
import time
from scrapy.exceptions import DropItem
import redis
from google.cloud import storage
from google.cloud import firestore
import google.cloud.exceptions
from scrapy.utils.conf import closest_scrapy_cfg
import os
from datetime import date
from dateutil.parser import parse
from jsonschema import validate, Draft3Validator, SchemaError, ValidationError
import jsonschema
import helpers
import urllib
import requests
import pandas as pd

logger = logging.getLogger(__name__)


class ProcessItem:

    def process_item(self, item, spider):
        _ = spider
        if item['producer_name'] == 'otodom':
            item = self.process_item_ototdom(item)
        elif item['producer_name'] == 'olx':
            item = self.process_item_olx(item)
        elif item['producer_name'] == 'gratka':
            item = self.process_item_gratka(item)
        elif item['producer_name'] == 'morizon':
            item = self.process_item_morizon(item)
        elif item['producer_name'] == 'plot_sprzedajemy':
            item = self.process_item_plot_sprzedajemy(item)
        elif item['producer_name'] == 'plot_gumtree':
            item = self.process_item_plot_gumtree(item)
        elif item['producer_name'] == 'plot_olx':
            item = self.process_item_plot_olx(item)
        elif item['producer_name'] == 'plot_gratka':
            item = self.process_item_plot_gratka(item)
        elif item['producer_name'] == 'plot_otodom':
            item = self.process_item_plot_ototdom(item)
        else:
            raise ValueError('There is no %s in ProcessItem' % item['producer_name'])
        return item

    def process_item_ototdom(self, item):

        item['tracking_id'] = item['tracking_id'].strip()
        item['price'] = helpers.Scraper.digits_from_str(item['price'], returntype=int)
        item['_id'] = ("oto_"+str(item["tracking_id"]) + "_" + str(item['price'])).strip()
        item['flat_size'] = helpers.Scraper.digits_from_str(item['flat_size'], returntype=int)
        item['rooms'] = helpers.Scraper.digits_from_str(item['rooms'], returntype=int)
        item['floor'] = helpers.Scraper.convert_floor(item['floor'])
        item['price_m2'] = helpers.Scraper.digits_from_str(item['price_m2'], returntype=int)
        item['number_of_floors'] = helpers.Scraper.convert_floor(item['number_of_floors'])
        item['year_of_building'] = helpers.Scraper.digits_from_str(item['year_of_building'], returntype=int)

        item['date_created'] = helpers.Scraper.datetime2str(item['date_created'])
        item['date_modified'] = helpers.Scraper.datetime2str(item['date_modified'])

        item['download_date'] = helpers.Scraper.datetime2str(helpers.Scraper.current_datetime())
        item['download_date_utc'] = time.time()
        return item

    def process_item_olx(self, item):

        item['tracking_id'] = item['tracking_id'].strip()
        item['price'] = helpers.Scraper.digits_from_str(item['price'], returntype=int)
        item['_id'] = ("olx_"+str(item["tracking_id"]) + "_" + str(item['price'])).strip()
        item['flat_size'] = helpers.Scraper.digits_from_str(item['flat_size'], returntype=int)
        item['rooms'] = helpers.Scraper.digits_from_str(item['rooms'], returntype=int)
        item['floor'] = helpers.Scraper.convert_floor(item['floor'])
        item['price_m2'] = helpers.Scraper.digits_from_str(item['price_m2'], returntype=int)
        item['number_of_floors'] = helpers.Scraper.digits_from_str(item['number_of_floors'], returntype=int)
        item['year_of_building'] = helpers.Scraper.digits_from_str(item['year_of_building'], returntype=int)

        item['download_date'] = helpers.Scraper.datetime2str(helpers.Scraper.current_datetime())
        item['download_date_utc'] = time.time()
        return item

    def process_item_gratka(self, item):

        item['tracking_id'] = str(item['tracking_id'])
        item['price'] = helpers.Scraper.digits_from_str(item['price'], returntype=int)
        item['_id'] = ("gra_"+str(item["tracking_id"]) + "_" + str(item['price'])).strip()
        item['flat_size'] = helpers.Scraper.digits_from_str(item['flat_size'], returntype=int)
        item['rooms'] = helpers.Scraper.digits_from_str(item['rooms'], returntype=int)
        item['floor'] = helpers.Scraper.convert_floor(item['floor'])
        item['price_m2'] = helpers.Scraper.digits_from_str(item['price_m2'], returntype=int)
        item['number_of_floors'] = helpers.Scraper.digits_from_str(item['number_of_floors'], returntype=int)
        item['year_of_building'] = helpers.Scraper.digits_from_str(item['year_of_building'], returntype=int)

        item['date_modified'] = helpers.Scraper.datetime2str(item['date_modified'])

        item['download_date'] = helpers.Scraper.datetime2str(helpers.Scraper.current_datetime())
        item['download_date_utc'] = time.time()
        return item

    def process_item_morizon(self, item):

        item['tracking_id'] = item['tracking_id'].strip()
        item['price'] = helpers.Scraper.digits_from_str(item['price'], returntype=int)
        item['_id'] = ("mor_"+str(item["tracking_id"]) + "_" + str(item['price'])).strip()
        item['flat_size'] = helpers.Scraper.digits_from_str(item['flat_size'], returntype=int)
        item['rooms'] = helpers.Scraper.digits_from_str(item['rooms'], returntype=int)
        item['floor'] = helpers.Scraper.convert_floor(item['floor'])
        item['price_m2'] = helpers.Scraper.digits_from_str(item['price_m2'], returntype=int)
        item['number_of_floors'] = helpers.Scraper.convert_floor(item['number_of_floors'])
        item['year_of_building'] = helpers.Scraper.digits_from_str(item['year_of_building'], returntype=int)

        item['date_created'] = helpers.Scraper.datetime2str(item['date_created'])
        item['date_modified'] = helpers.Scraper.datetime2str(item['date_modified'])

        item['download_date'] = helpers.Scraper.datetime2str(helpers.Scraper.current_datetime())
        item['download_date_utc'] = time.time()
        return item

    def process_item_plot_sprzedajemy(self, item):

        item['tracking_id'] = item['tracking_id'].strip()
        item['price'] = helpers.Scraper.digits_from_str(item['price'], returntype=int)
        item['_id'] = ("sprz_d_"+str(item["tracking_id"]) + "_" + str(item['price'])).strip()
        item['size'] = helpers.Scraper.digits_from_str(item['size'], returntype=int)
        item['price_m2'] = helpers.Scraper.digits_from_str(item['price_m2'], returntype=int)

        item['date_modified'] = helpers.Scraper.datetime2str(item['date_modified'])

        item['download_date'] = helpers.Scraper.datetime2str(helpers.Scraper.current_datetime())
        item['download_date_utc'] = time.time()

        return item

    def process_item_plot_gumtree(self, item):

        item['tracking_id'] = item['tracking_id'].strip()
        item['price'] = helpers.Scraper.digits_from_str(item['price'], returntype=int)
        item['_id'] = ("gum_d_"+str(item["tracking_id"]) + "_" + str(item['price'])).strip()
        item['size'] = helpers.Scraper.digits_from_str(item['size'], returntype=int)
        item['date_created'] = helpers.Scraper.datetime2str(item['date_created'])
        item['download_date'] = helpers.Scraper.datetime2str(helpers.Scraper.current_datetime())
        item['download_date_utc'] = time.time()
        return item

    def process_item_plot_olx(self, item):

        item['tracking_id'] = item['tracking_id'].strip()
        item['price'] = helpers.Scraper.digits_from_str(item['price'], returntype=int)
        item['_id'] = ("olx_d_"+str(item["tracking_id"]) + "_" + str(item['price'])).strip()
        item['size'] = helpers.Scraper.digits_from_str(item['size'], returntype=int)
        item['price_m2'] = helpers.Scraper.digits_from_str(item['price_m2'], returntype=int)
        item['download_date'] = helpers.Scraper.datetime2str(helpers.Scraper.current_datetime())
        item['download_date_utc'] = time.time()
        return item

    def process_item_plot_gratka(self, item):

        item['tracking_id'] = str(item['tracking_id'])
        item['price'] = helpers.Scraper.digits_from_str(item['price'], returntype=int)
        item['_id'] = ("gra_d_"+str(item["tracking_id"]) + "_" + str(item['price'])).strip()
        item['size'] = helpers.Scraper.digits_from_str(item['size'], returntype=int)
        item['price_m2'] = helpers.Scraper.digits_from_str(item['price_m2'], returntype=int)
        item['date_modified'] = helpers.Scraper.datetime2str(item['date_modified'])
        item['download_date'] = helpers.Scraper.datetime2str(helpers.Scraper.current_datetime())
        item['download_date_utc'] = time.time()
        return item

    def process_item_plot_ototdom(self, item):

        item['tracking_id'] = item['tracking_id'].strip()
        item['price'] = helpers.Scraper.digits_from_str(item['price'], returntype=int)
        item['_id'] = ("oto_d_"+str(item["tracking_id"]) + "_" + str(item['price'])).strip()
        item['size'] = helpers.Scraper.digits_from_str(item['size'], returntype=int)
        item['price_m2'] = helpers.Scraper.digits_from_str(item['price_m2'], returntype=int)
        item['date_created'] = helpers.Scraper.datetime2str(item['date_created'])
        item['date_modified'] = helpers.Scraper.datetime2str(item['date_modified'])
        item['download_date'] = helpers.Scraper.datetime2str(helpers.Scraper.current_datetime())
        item['download_date_utc'] = time.time()
        return item


class ProcessItemGeocode:

    def process_item(self, item, spider):
        _ = spider

        item['geo_coordinates'], \
            item['geo_address_text'], item['geo_address_coordin'] = \
            helpers.Geodata.get_geocode_openstreet(item['geo_coordinates'])
        item['GC_latitude'] = float(item['geo_coordinates']['latitude'])
        item['GC_longitude'] = float(item['geo_coordinates']['longitude'])
        item['GC_boundingbox'] = item['geo_address_coordin']['@boundingbox']
        item['GC_addr_house_number'] = \
            item['geo_address_text']['house_number'] if 'house_number' \
            in item['geo_address_text'] else None
        item['GC_addr_road'] = item['geo_address_text']['road'] if 'road' \
            in item['geo_address_text'] else None
        item['GC_addr_neighbourhood'] = \
            item['geo_address_text']['neighbourhood'] if 'neighbourhood' \
            in item['geo_address_text'] else None
        item['GC_addr_suburb'] = item['geo_address_text']['suburb'] \
            if 'suburb' in item['geo_address_text'] else None
        item['GC_addr_city'] = item['geo_address_text']['city'] \
            if 'city' in item['geo_address_text'] else None
        item['GC_addr_state'] = item['geo_address_text']['state'] \
            if 'state' in item['geo_address_text'] else None
        item['GC_addr_postcode'] = item['geo_address_text']['postcode'] \
            if 'postcode' in item['geo_address_text'] else None
        item['GC_addr_country'] = item['geo_address_text']['country'] \
            if 'country' in item['geo_address_text'] else None
        item['GC_addr_country_code'] = \
            item['geo_address_text']['country_code'] if 'country_code' \
            in item['geo_address_text'] else None
        _ = item.pop('geo_coordinates')
        _ = item.pop('geo_address_coordin')
        _ = item.pop('geo_address_text')

        return item


class OutputLocal:

    def __init__(self, encoding, file_dir, file_name, file_adddate2name,
                 **kwargs):
        self.encoding = encoding
        self.file_dir = file_dir
        self.file_name = file_name
        self.file_adddate2name = file_adddate2name
        self.file = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            encoding=crawler.settings.get('FEED_EXPORT_ENCODING'),
            file_dir=crawler.settings.get('LOCAL_FILE_DIR'),
            file_name=crawler.settings.get('LOCAL_FILE_NAME'),
            file_adddate2name=crawler.settings.get('ADDDATE2NAME')
        )

    def process_item(self, item, spider):
        _ = spider

        producer = item['producer_name']

        today = date.today().strftime("%Y%m%d")

        if self.file_adddate2name:
            file_path = os.path.join(
                self.file_dir, self.file_name+"_"+today+".jsonline")
        else:
            file_path = os.path.join(self.file_dir, self.file_name+".jsonline")

        file = codecs.open(file_path, 'a', encoding=self.encoding)
        logger.info("{}: Local jsonline: save offer {}, url {}".format(producer,
                                                               item['_id'],item['url']))
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        file.write(line)
        file.close()

        return item


class OutputStdout:

    def process_item(self, item, spider):
        _ = spider
        _tmp = item.copy()
        line = json.dumps(dict(_tmp), ensure_ascii=False)
        print(line)
        return item


class OutputRedis():

    def __init__(self, host, port, db, id_field):
        self.host = host
        self.port = port
        self.db = db
        self.id_field = id_field
        self.r = redis.Redis(host=self.host, port=self.port, db=self.db)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('REDIS_HOST'),
            port=crawler.settings.get('REDIS_PORT'),
            db=crawler.settings.get('REDIS_DB_INDEX'),
            id_field=crawler.settings.get('ID_FIELD')
        )

    def process_item(self, item, spider):

        _ = spider
        producer = item['producer_name']

        try:
            self.r.set(item[self.id_field], 1)
            logger.info("{}: Redis: add to cache {}".format(
                producer, item[self.id_field]))
        except (redis.ConnectionError) as e:
            logger.error("%s: Could not connect to server: %s" % (producer, e))
        except BaseException as e:
            logger.error(item[self.id_field])
            logger.error("%s: BaseException at Redis, something went wrong: %s"
                         % (producer, e))
        return item


class CheckIfExistRedis(OutputRedis):

    def process_item(self, item, spider):

        _ = spider
        producer = item['producer_name']

        try:
            if ("found" in item) and ("cache" not in item):
                self.r.set(item[self.id_field], 1)
                logger.info("{}: Redis: add to cache {}".format(producer,
                            item[self.id_field]))
            elif self.r.exists(item[self.id_field]) and ("cache" not in item):
                item["found"] = True
                item["cache"] = True
                logger.info("{}: Redis: found {} ".format(producer,
                            item[self.id_field]))
        except (redis.ConnectionError) as e:
            logger.error("%s: Could not connect to server: %s" % (producer, e))
        except BaseException as e:
            logger.error(item[self.id_field])
            logger.error("%s: BaseException at Redis, something went wrong: %s"
                         % (producer, e))
        return item


class UpdateExistRedis(CheckIfExistRedis):
    pass


class OutputGCPFirestore():

    def __init__(self, collection, id_field, drop_keys, str2date, secters_path):
        self.collection = collection
        self.id_field = id_field
        self.drop_keys = drop_keys
        self.str2date = str2date
        self.secters_path = secters_path
        self.db = firestore.Client.from_service_account_json(secters_path)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            collection=crawler.settings.get('COLLECTION'),
            id_field=crawler.settings.get('ID_FIELD'),
            drop_keys=crawler.settings.get('FIRESTORE_KEYS_MOVE_2_MORE'),
            str2date=crawler.settings.get('FIRESTORE_STR2DATE'),
            secters_path=crawler.settings.get('SECRETS_PATH')
        )

    def process_item(self, item, spider):

        _ = spider
        try:
            producer = item['producer_name']
        except BaseException:
            producer = "Unknow"

        try:
            tmp = item.copy()
            more = dict()
            for key in self.drop_keys:
                more[key] = tmp.pop(key)

            for key in self.str2date:
                tmp[key] = parse(tmp[key]) if tmp[key] else None

            doc_lv1 = self.db.collection(self.collection).\
                document(item[self.id_field])
            doc_lv1.set(tmp)
            doc_lv2 = doc_lv1.collection('more').document('data')
            doc_lv2.set(more)

            logger.info("{}: Firestore: added {} to collection {}".format(
                producer, item[self.id_field], self.collection))

        except (google.cloud.exceptions.Forbidden,
                google.cloud.exceptions.Unauthorized) as e:
            logger.error("%s Could not connect to Firestore server: %s" %
                         (producer, e))

        except BaseException as e:
            logger.error(item[self.id_field])
            logger.error("%s: BaseException at GCP Firestore (check " +
                         "existence) something went wrong: %s" % (producer, e))
        return item


class CheckIfExistGCPFirestore(OutputGCPFirestore):

    def process_item(self, item, spider):

        _ = spider
        try:
            producer = item['producer_name']
        except BaseException:
            producer = "Unknow"

        try:
            if "found" not in item:
                result = self.db.collection(self.collection).\
                    document(item[self.id_field]).get([]).exists

                if result:
                    item['found'] = True
                    logger.info("{}: Firestore: found {} ".format(producer,
                                item[self.id_field]))

        except (google.cloud.exceptions.Forbidden,
                google.cloud.exceptions.Unauthorized) as e:
            logger.error("%s: Could not connect to server: %s" % (producer, e))

        except BaseException as e:
            logger.error(item[self.id_field])
            logger.error("%s: BaseException at GCP Firestore (check " +
                         "existence) something went wrong: %s" % (producer, e))

        return item


class OutputFilter:

    def __init__(self, schema_file_name):
        self.schema_file_name = schema_file_name
        self.file_path = os.path.join(
            os.path.dirname(closest_scrapy_cfg()), "helpers", schema_file_name)
        self.schema = self._load_schema()
        self.valid = Draft3Validator(self.schema)

    def _load_schema(self):
        with open(self.file_path, "r") as file:
            schema = json.load(file)
        _ = schema['properties'].pop('GC_latitude')
        _ = schema['properties'].pop('GC_longitude')
        _ = schema['properties'].pop('GC_boundingbox')
        _ = schema['properties'].pop('GC_addr_road')
        _ = schema['properties'].pop('GC_addr_neighbourhood')
        _ = schema['properties'].pop('GC_addr_suburb')
        _ = schema['properties'].pop('GC_addr_city')
        _ = schema['properties'].pop('GC_addr_state')
        _ = schema['properties'].pop('GC_addr_postcode')
        _ = schema['properties'].pop('GC_addr_country')
        _ = schema['properties'].pop('GC_addr_country_code')

        return schema

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            schema_file_name=crawler.settings.get('SCHEMA_FILE_NAME')
        )

    def process_item(self, item, spider):

        try:
            producer = item['producer_name']
        except BaseException:
            producer = "Unknow"

        if "found" in item:
            raise DropItem("{}: Found Drop {}!".format(producer, item['_id']))

        elif not self.valid.is_valid(item):
            errors = sorted(self.valid.iter_errors(item),
                            key=lambda e: e.absolute_path)
            errors_plain = "\n".join([(e.relative_path[-1]+" -> "+e.message)
                                      for e in errors])
            logger.info(errors_plain)
            raise DropItem("{}: Invalid schema Drop {}!".format(producer,
                                                                item['_id']))
        else:
            return item


class ValidSchema(OutputFilter):

    def _load_schema(self):
        with open(self.file_path, "r") as file:
            schema = json.load(file)
        return schema


class OrderbySchema(OutputFilter):

    def process_item(self, item, spider):

        try:
            producer = item['producer_name']
        except BaseException:
            producer = "Unknow"

        keys_schema = sorted(self.schema.keys(), key=lambda x: x.lower())
        keys_item = sorted(item.keys(), key=lambda x: x.lower())

        tmp = dict()

        for key in keys_schema:
            if key in keys_item:
                tmp[key] = item[key]
                _ = keys_item.pop(key)

        for key in keys_item:
            tmp[key] = item[key]

        #_ = tmp.pop('additional_info')
        #_ = tmp.pop('body')
        #_ = tmp.pop('description')

        return tmp


class SendTelegramMessage:

    def __init__(self, key_path, keywords_flats, query_flats,
                 keywords_plots, query_plots):
        self.key_path = key_path
        self.keywords_flats = keywords_flats
        self.query_flats = query_flats
        self.keywords_plots = keywords_plots
        self.query_plots = query_plots

        if os.path.exists(self.key_path):
            with open(self.key_path, "r") as file:
                self.telegram_key = json.load(file)
        else:
                self.telegram_key = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            key_path=crawler.settings.get('TELEGRAM_KEY_PATH'),
            keywords_flats=crawler.settings.get('TELEGRAM_FLATS_KEYWORDS'),
            query_flats=crawler.settings.get('TELEGRAM_FLATS_QUERY'),
            keywords_plots=crawler.settings.get('TELEGRAM_PLOTS_KEYWORDS'),
            query_plots=crawler.settings.get('TELEGRAM_PLOTS_QUERY'),
        )

    def process_item(self, item, spider):
        _ = spider

        try:
            producer = item['producer_name']
        except BaseException:
            producer = "Unknow"

        import math

        if 'plot' in item['producer_name']:

            df = pd.DataFrame([item])

            keywords = self.keywords_plots
            query = self.query_plots
            key = self.telegram_key['key']
            chat_id = self.telegram_key['chat_id']

            df = df.assign(
                distance=lambda x: x.apply(
                    lambda x: helpers.Geodata.haversine(
                        x['GC_latitude'], x['GC_longitude']), axis=1)
                        )

            for i, row in df.query(query).iterrows():
                name = row['name'].strip()
                price = row['price']
                url = row['url']
                id_ = row['_id']
                distance = df.distance
                description = (row['description'].strip()[
                    :min(len(row['description']), 150)])

                text = 'Znalazlem dzialke: \n' +  \
                    'Cena: ' + str(price) + ' pln' + ' \n ' + \
                    'Odleglos od Warszawy: %d km \n' % distance + \
                    f'>>{{"id":"{id_}"}}<< \n ' + \
                    url

                if re.search(keywords, row['name'] + " " + row['description'],
                             re.IGNORECASE):
                    logger.info("%s: Telegram sent message %s: %s" % (producer, row['_id'], text))
                    urltmp = 'https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s'
                    url = urltmp % (key, chat_id,
                                    urllib.parse.quote_plus(text))
                    _ = requests.get(url, timeout=10)

        return item
