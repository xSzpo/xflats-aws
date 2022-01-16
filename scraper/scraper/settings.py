import os
# -*- coding: utf-8 -*-

# Scrapy settings for app_webscr_pipe_otodom project
#
# You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

##################
# GENERAL SETTINGS
##################

SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'
LOG_LEVEL = 'INFO'
LOG_FORMATTER = 'helpers.base.PoliteLogFormatter'
FEED_EXPORT_ENCODING = "UTF-8"
#LOCAL_SECRETS = "/Users/dsz/gdrive-priv/My Drive/01_Projects/202003_xFlats_K8S/secrets"
LOCAL_SECRETS = "/scraper/secrets"

################
# CRAWL SETTINGS
################

COOKIES_ENABLED = False
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 4
DOWNLOAD_DELAY = 3
LOGSTATS_INTERVAL = 0
CRAWL_LIST_PAGES = 99  # how many pages with links ]to crawl (start pages)


###################
# PRODUCER SETTINGS
###################

BOT_NAME = 'xname'

#################
# OUTPUT SETTINGS
#################

# SELECT WHERE TO CHECK
SOURCE = 'LOCAL'

ID_FIELD = '_id'
DOWNLOAD_DATE = 'download_date'

# REDIS
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB_INDEX = 0

# S3
BUCKET_NAME = 'mojewiadroxszpo'

# GCP Firestore
COLLECTION = 'flats'
SECRETS_PATH = f"{LOCAL_SECRETS}/gcpfirestore_key.json"
FIRESTORE_KEYS_MOVE_2_MORE = ['body']
FIRESTORE_STR2DATE = ['download_date', 'date_created', 'date_modified']

# local

#LOCAL_FILE_DIR = "/Users/danielszponar/GoogleDrive/01_Projects/202003_xFlats_K8S/scraper/data/"
LOCAL_FILE_DIR = "data_flats"
LOCAL_FILE_NAME = "data_plots"
ADDDATE2NAME = True

# schema
SCHEMA_FILE_NAME = 'schema_plot.json'

# schema
TELEGRAM_KEY_PATH = f"{LOCAL_SECRETS}/telegram_key.json"
TELEGRAM_FLATS_KEYWORDS = ""
TELEGRAM_FLATS_QUERY = ""
TELEGRAM_PLOTS_KEYWORDS = "rzek.|brzeg|jeziorem|jezioro|jeziorami|pla.z|zalew|narew|narwi|bug|wkr.|wisl|zegrz"
TELEGRAM_PLOTS_QUERY = "distance <150 and price <150000"

##########
# PIELINES
##########

ITEM_PIPELINES = {
    'scraper.pipelines.ProcessItem': 100,
    'scraper.pipelines.CheckIfExistRedis': None,
    'scraper.pipelines.CheckIfExistGCPFirestore': None,
    'scraper.pipelines.UpdateExistRedis': None,
    'scraper.pipelines.OutputFilter': 130,
    'scraper.pipelines.ProcessItemGeocode': 140,
    'scraper.pipelines.ValidSchema': 150,
    'scraper.pipelines.OrderbySchema': 160,
    'scraper.pipelines.SendTelegramMessage': 165,
    'scraper.pipelines.OutputLocal': 170,
    'scraper.pipelines.OutputGCPFirestore': None,
    'scraper.pipelines.OutputRedis': None,
    'scraper.pipelines.OutputStdout': None
}

# -----------------------------------------------------------------------------
# USER AGENT
# -----------------------------------------------------------------------------

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_useragents.downloadermiddlewares.useragents.UserAgentsMiddleware': 500,
}

USER_AGENTS = [
    ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
     '(KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'),
    ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
     '(KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 OPR/76.0.4017.137'),
    ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 '
     '(KHTML, like Gecko) Version/14.1 Safari/605.1.15')
]
