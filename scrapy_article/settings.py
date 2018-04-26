# -*- coding: utf-8 -*-
import os
import sys
BASE_DIR = os.path.realpath(os.path.dirname(__file__))

sys.path.insert(0, BASE_DIR)
# Scrapy settings for scrapy_article project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'scrapy_article'

SPIDER_MODULES = ['scrapy_article.spiders']
NEWSPIDER_MODULE = 'scrapy_article.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'scrapy_article (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'scrapy_article.middlewares.ScrapyArticleSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   # 'scrapy_article.middlewares.ScrapyArticleDownloaderMiddleware': 543,
   'scrapy_article.middlewares.LagouDownloaderMiddleware': 543,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   # 'scrapy_article.pipelines.ScrapyArticlePipeline': 300,
    # 'scrapy.pipelines.images.ImagesPipeline': 1,
    # 'scrapy_article.pipelines.ImageJobbolePipeline': 1,
    # 'scrapy_article.pipelines.JsonJobbolePipline': 10,
    # 'scrapy_article.pipelines.JsonJobboleExportPipline': 10,
    # 'scrapy_article.pipelines.MysqlPipeline': 10,
    'scrapy_article.pipelines.MysqlTwistedPipeline': 10,
}
IMAGES_RESULT_FIELD = 'front_image_path'
IMAGES_URLS_FIELD = 'front_image_url'
IMAGES_STORE = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'images')
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

MYSQL_INFO = dict(
    host='rm-uf69d6mp154aocu5tbo.mysql.rds.aliyuncs.com',
    user='root',
    password='123QWEqwe',
    db='article_spider',
    charset='utf8',
    use_unicode=True,
    )

SQL_DATE_TIME = '%Y-%m-%d %H:%M:%S'
SQL_DATE = '%Y-%m-%d'
