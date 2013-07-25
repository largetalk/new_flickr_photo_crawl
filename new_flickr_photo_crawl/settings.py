# Scrapy settings for new_flickr_photo_crawl project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'new_flickr_photo_crawl'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['new_flickr_photo_crawl.spiders']
NEWSPIDER_MODULE = 'new_flickr_photo_crawl.spiders'
#USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.54 Safari/536.5'
COOKIES_ENABLED = True

