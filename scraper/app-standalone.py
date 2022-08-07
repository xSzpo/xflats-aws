#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This is a awesome python script thats scraps www"""

from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from twisted.internet.task import deferLater
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
import json
import time
import os

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

configure_logging()


def env2pipe(val, default=0):
    x = os.getenv(val, default)
    if x == "None":
        return None
    else:
        return int(x)


def scraper(event={}, context={}):

    _, _ = event, context

    settings = get_project_settings()
    settings['REDIS_HOST'] = os.getenv('REDIS_HOST', 'redis')
    settings['REDIS_PORT'] = int(os.getenv('REDIS_PORT', '6379'))
    settings['REDIS_DB_INDEX'] = int(os.getenv('REDIS_DB_INDEX', '0'))

    # CRAWL SETTINGS
    settings['SAVE_BODY'] = int(os.getenv('SAVE_BODY', True))

    # local
    settings['LOCAL_FILE_DIR'] = os.getenv("JSONLINE_FILE_DIR","/app/data")
    settings['LOCAL_FILE_NAME'] = os.getenv("JSONLINE_FILE_NAME", "data_flats")
    settings['ADDDATE2NAME'] = bool(os.getenv("JSONLINE_ADDDATE2NAME",
                                              "True") == "True")

    # telegram
    settings['TELEGRAM_KEY_PATH'] = os.getenv('TELEGRAM_KEY_PATH',
        "/app/secrets/telegram_key.json")
    settings['TELEGRAM_FLATS_KEYWORDS'] = os.getenv('TELEGRAM_FLATS_KEYWORDS', "")
    settings['TELEGRAM_FLATS_QUERY'] = os.getenv('TELEGRAM_FLATS_QUERY', "")
    settings['TELEGRAM_PLOTS_KEYWORDS'] = os.getenv('TELEGRAM_PLOTS_KEYWORDS', "rzek|rzec|lini\w+\W+brzeg|jezio")
    settings['TELEGRAM_PLOTS_QUERY'] = os.getenv('TELEGRAM_PLOTS_QUERY', "distance <200 and price <150000")

    # scraper config
    settings['CRAWL_LIST_PAGES'] = int(os.getenv("SCRAPER_CRAWL_LIST_PAGES",
                                                 "2"))
    settings['CONCURRENT_REQUESTS'] = int(
        os.getenv("SCRAPER_CONCURRENT_REQUESTS", "1"))

    settings['ITEM_PIPELINES'] = {
        'scraper.pipelines.ProcessItem': env2pipe("scr_pipe_ProcessItem",
                                                  "100"),
        'scraper.pipelines.CheckIfExistRedis': env2pipe(
            "scr_pipe_CheckIfExistRedis", "None"),
        'scraper.pipelines.CheckIfExistGCPFirestore': env2pipe(
            "scr_pipe_CheckIfExistGCPFirestore", "None"),
        'scraper.pipelines.UpdateExistRedis': env2pipe(
            "scr_pipe_UpdateExistRedis", "None"),
        'scraper.pipelines.OutputFilter': env2pipe("scr_pipe_OutputFilter",
                                                   "130"),
        'scraper.pipelines.ProcessItemGeocode': env2pipe(
            "scr_pipe_ProcessItemGeocode", "140"),
        'scraper.pipelines.ValidSchema': env2pipe("scr_pipe_ValidSchema",
                                                  "150"),
        'scraper.pipelines.OrderbySchema': env2pipe("scr_pipe_OrderbySchema",
                                                    "160"),
        'scraper.pipelines.SendTelegramMessage': env2pipe("scr_pipe_SendTelegramMessage",
                                                    "165"),
        'scraper.pipelines.OutputLocal': env2pipe("scr_pipe_OutputLocal",
                                                  "170"),
        'scraper.pipelines.OutputGCPFirestore': env2pipe(
            "scr_pipe_OutputGCPFirestore", "None"),
        'scraper.pipelines.OutputRedis': env2pipe("scr_pipe_OutputRedis",
                                                  "None"),
        'scraper.pipelines.OutputStdout': env2pipe("scr_pipe_OutputStdout",
                                                   "None"),
    }

    # wait until other ysstems are ready
    sleep_time = int(os.getenv('SCRAPER_START_DELAY_SEC', "0"))
    time.sleep(sleep_time)

    scrapy_del = int(os.getenv('SCRAPER_DELAY_AFTER_EACH_RUN_SEC', "60"))

    process = CrawlerProcess(settings)

    def crash(failure):
        print('oops, spider crashed')
        print(failure.getTraceback())

    def sleep(*args, seconds):
        """Non blocking sleep callback"""
        return deferLater(reactor, seconds, lambda: None)

    def _crawl(result, spider):
        deferred = process.crawl(spider)
        deferred.addCallback(
            lambda results: print('waiting %d seconds before restart...' %
                                  scrapy_del))
        deferred.addErrback(crash)  # <-- add errback here
        deferred.addCallback(sleep, seconds=scrapy_del)
        deferred.addCallback(_crawl, spider)
        return deferred

    spiders = os.getenv("SCRAPER_CRAWLER_NAME", "olx, otodom, gratka, morizon")

    for spider_name in [i.strip() for i in spiders.split(",")]:
        _crawl(None, spider_name)

    process.start()

    return {
        'statusCode': 200,
        'body': json.dumps('scraping successful')
    }


if __name__ == "__main__":

    scraper()
