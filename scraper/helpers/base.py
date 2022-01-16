import logging
import os
import datetime
import requests
import xmltodict
import re
from functools import reduce
import codecs
import pytz
import gc
import math
from dateutil.parser import parse
from scrapy import logformatter
from scrapy.exceptions import DropItem

logger = logging.getLogger(__name__)


class PoliteLogFormatter(logformatter.LogFormatter):
    def dropped(self, item, exception, response, spider):
        if '_id' in item.keys():
            return {
                'level': logging.INFO,
                'msg': u"Dropped item %s, %s" % (item['_id'],item['url']),
                'args': {
                    'exception': exception,
                    'item': item,
                }
            }
        else:
            return {
                'level': logging.INFO,
                'msg': u"Dropped item, exception: %s" % exception,
                'args': {
                    'exception': exception,
                    'item': item,
                }
            }


class Time:

    @staticmethod
    def timer(start, end):
        hours, rem = divmod(end-start, 3600)
        minutes, seconds = divmod(rem, 60)
        return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds)


class Scraper:

    @staticmethod
    def current_timestamp():
        return int(datetime.datetime.now().timestamp())

    @staticmethod
    def current_datetime():
        return datetime.datetime.utcnow()
        # return datetime.datetime.now(pytz.timezone("Europe/Warsaw"))

    @staticmethod
    def datetime2str(dt):
        if isinstance(dt, datetime.datetime):
            return dt.__str__()

    @staticmethod
    def timestamp2datetime(timestamp):
        return datetime.datetime.fromtimestamp(timestamp)

    @staticmethod
    def contains_digit(x):
        return any([i.isdigit() for i in x])

    @staticmethod
    def dict_except(dictionary, except_keys=[], include_keys=None):
        temp = {}
        for key in dictionary:
            if key not in except_keys:
                if include_keys is None:
                    temp[key] = dictionary[key]
                else:
                    if key in include_keys:
                        temp[key] = dictionary[key]
        return temp

    @staticmethod
    def concat_dict(dict_list):
        return reduce(lambda x, y: dict(x, **y), dict_list)

    @staticmethod
    def digits_from_str(txt, returntype=float):
        """return numbers from string '523 000 zł' -> 523000,

        :param:
        txt - text that contains number
        :return:
        int
        """
        if txt and re.search('[\d., ]{1,}', txt):
            result = re.sub(",", ".", re.sub(r" +", "", re.findall('[\d., ]{1,}', txt)[-1]))
            if len(result) == 0:
                return None
            else:
                if returntype == int:
                    return int(float(result))
                elif returntype == float:
                    return float(result)
        else:
            return None

    @staticmethod
    def convert_floor(x):
        if x:
            if str(x).strip().isdigit():
                return int(x)
            elif x.lower() == 'parter':
                return int(0)
            elif x.lower() == 'suterena':
                return None
            elif x == '> 10':
                return int(11)
            elif x.lower() == 'powyżej 10':
                return int(11)
            elif x.lower() == 'powyżej 30':
                return int(11)
            elif x == 'poddasze':
                return None
            elif type(x) == str:
                return Scraper.digits_from_str(x)
            else:
                return None
        else:
            return None

    @staticmethod
    def get_createdate_polish_months(data):

        logger.debug(data)
        if data:
            reg = r"[0123]?\d\W+\S+\W+20\d\d"
            match = re.search(reg, data.lower())
            if match:
                x = match.group(0)
                logger.debug(x)
                x = re.sub(r"stycz\S+", "jan", x)
                x = re.sub(r"lut\S+", "feb", x)
                x = re.sub(r"mar\S+", "mar", x)
                x = re.sub(r"kwie\S+", "apr", x)
                x = re.sub(r"maj\S+", "may", x)
                x = re.sub(r"czerw\S+", "jun", x)
                x = re.sub(r"lip\S+", "jul", x)
                x = re.sub(r"sierp\S+", "aug", x)
                x = re.sub(r"wrze\S+", "sep", x)
                x = re.sub(r"pa.dziern\S+", "oct", x)
                x = re.sub(r"listopa\S+", "nov", x)
                x = re.sub(r"grud\S+", "dec", x)
                logger.debug(x)

                try:
                    x = parse(x)
                    x = Scraper.datetime2str(x)
                    logger.debug(x)
                    return x
                except BaseException:
                    logger.error(x)
                    return None

            else:
                return None
        else:
            return None

    @staticmethod
    def searchregex(txt, pattern, group=0, func=None):
        if txt:
            match = re.search(pattern, txt)
            if match and func:
                return func(match.group(group))
            elif match:
                return match.group(group)
            else:
                return None
        else:
            return None


class Geodata:

    @staticmethod
    def get_geodata_otodom(content):

        pattern = "latitude.:(\d\d.\d+),.longitude.:(\d\d.\d+)"
        if re.search(pattern, content.decode("utf-8")):
            geocoordinates = dict()
            geocoordinates['latitude'] = Scraper.searchregex(
                content.decode("utf-8"),"latitude.:(\d\d.\d+)", group=1)
            geocoordinates['longitude'] = Scraper.searchregex(
                content.decode("utf-8"),"longitude.:(\d\d.\d+)", group=1)
            return geocoordinates
        else:
            return dict()

    @staticmethod
    def get_geodata_olx(content):

        pattern = r'{\W+zoom\W+\d+\W+lat\W+(\d+.\d+)\W+lon\W+(\d+.\d+)'
        match = re.search(pattern, content.decode("utf-8"))
        if match:
            data_lat = float(match.group(1))
            data_lon = float(match.group(2))
            geocoordinates = {"latitude": data_lat, "longitude": data_lon}
            return geocoordinates
        else:
            return dict()

        @staticmethod
        def get_geodata_gratka(content):

            pattern = "szerokosc-geograficzna-y..[\d]{2}\\.[\d]+"
            if re.search(pattern, content.decode("utf-8")):
                data_lat = re.findall("szerokosc-geograficzna-y..[\d]{2}\\.[\d]+", content.decode("utf-8"))[0]
                data_lat = "".join([i for i in data_lat if i.isdigit() or i == "."])
                data_lon = re.findall("dlugosc-geograficzna-x..[\d]{2}\\.[\d]+", content.decode("utf-8"))[0]
                data_lon = "".join([i for i in data_lon if i.isdigit() or i == "."])
                geocoordinates = {"latitude": data_lat, "longitude": data_lon}
                return geocoordinates
            else:
                return dict()

    @staticmethod
    def get_geocode_openstreet(geocoordinates):

        try:
            address = requests.get(
                "https://nominatim.openstreetmap.org/reverse?format=xml&lat={latitude}&lon={longitude}&zoom=18&addressdetails=1".format(
                    **geocoordinates)
            )

            address_text = xmltodict.parse(address.content)['reversegeocode']['addressparts']

            address_coordin = xmltodict.parse(address.content)['reversegeocode']['result']

            return geocoordinates, address_text, address_coordin
        except BaseException as e:
            raise DropItem("Openstreetmap error, %s " % e)

    @staticmethod
    def haversine(GC_latitude, GC_longitude):
        """calculates distance between coordinates and Warsaw, Jana Kazmierza

        Parameters
        ----------
        GC_latitude : float
            latitude ex. 52.22264693429859
        GC_longitude : float
            longitude, ex. 20.938653945922855

        Returns
        -------
        int
            distance in kilometers
        """

        R = 6372800  # Earth radius in meters
        lat1, lon1 = (52.22264693429859, 20.938653945922855)
        lat2, lon2 = (GC_latitude, GC_longitude)

        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi/2)**2 + \
            math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2

        return int(2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))/1000)
