#!/usr/bin/env python
# encoding=utf-8

from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.http import FormRequest
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from new_flickr_photo_crawl.items import PhotoItem, PhotoSetItem
from scrapy import log
import sys
import re
import sqlite3
### Kludge to set default encoding to utf-8
reload(sys)
sys.setdefaultencoding('utf-8')
 
class FlickrSpider(CrawlSpider):
    name = "flickr"
    allowed_domains = ["www.flickr.com", "staticflickr.com"]
    start_urls = [
            #"http://www.flickr.com/photos/largetalk/sets/"
    ]
    rules = [
            Rule(SgmlLinkExtractor(allow=['/photos/\w+/\d+/in/set-\d+']), 'parse_image'),
            Rule(SgmlLinkExtractor(allow=['/photos/\w+/sets/\d+/$']), 'parse_set')
    ]

    def __init__(self, username='largetalk', *args, **kwargs):
        super(FlickrSpider, self).__init__(*args, **kwargs)
        self.username = username
        self.start_urls = [
                "http://www.flickr.com/photos/%s/sets/" % username
        ]
        self.conn = sqlite3.connect('photo.db')
        self._create_table()
        self.photo_store = PhotoStore(username)

    def _create_table(self):
        sql1 = '''
        drop table if exists photos;
        '''
        sql2 = '''
        create table if not exists photos (
        photo_id text,
        web_url text,
        name  text,
        set_id text,
        set_name text,
        osize_url text,
        download_url text
        );
        '''

        sql3 = '''
        drop table if exists sets;
        '''
        sql4 = '''
        create table if not exists sets (
        set_id text,
        set_name text,
        photo_count text
        );
        '''
        self.conn.execute(sql1)
        self.conn.execute(sql2)
        self.conn.execute(sql3)
        self.conn.execute(sql4)
        self.conn.commit()

        #self.rules = [
        #        Rule(SgmlLinkExtractor(allow=['/photos/%s/page\d+/' % username])),
        #        Rule(SgmlLinkExtractor(allow=['/photos/%s/\d+/in/photostream' % username]), 'parse_image')
        #]

    def parse_set(self, response):
        set_id = response.url.split('/')[-2]
        hxs = HtmlXPathSelector(response)

        item = PhotoSetItem()
        item['set_id'] = set_id
        item['set_name'] = hxs.select("//h1[@class='set-title']/text()").extract()[0]
        item['photo_count'] = 0
        sql = "insert into sets (set_id, set_name, photo_count) values ('%s', '%s', '%s')" % (item['set_id'], item['set_name'].replace("'", "''"), item['photo_count'])
        self.conn.execute(sql)
        self.conn.commit()

        reg = re.compile('/photos/%s/\d+/in/set-%s' %(self.username, set_id))
        for url in reg.findall(response.body):
            yield Request('http://www.flickr.com' + url)

        yield item


    def parse_image(self, response):
        hxs = HtmlXPathSelector(response)

        item = PhotoItem()
        item['web_url'] = response.url
        photo_id =  response.url.split('/')[-3]
        set_id = response.url.split('/')[-1][4:]
        item['photo_id'] = photo_id
        item['name'] = hxs.select("//h1[@id='title_div']/text()").extract()[0]
        item['set_id'] = set_id
        cursor = self.conn.cursor()
        select_sql = "select set_name from sets where set_id = %s" % set_id
        cursor.execute(select_sql)
        row = cursor.fetchone()
        set_name = row[0] if row else 'UNKNOW'

        item['set_name'] = set_name
        item['osize_url'] =  "http://www.flickr.com/photos/%s/%s/sizes/o/in/set-%s/" % (self.username, photo_id, set_id)
        sql = "insert into photos (photo_id, web_url, name, set_id, set_name, osize_url) values ('%s', '%s', '%s', '%s', '%s', '%s')" % (photo_id, item['web_url'], item['name'], set_id, set_name, item['osize_url'])
        self.conn.execute(sql)
        self.conn.commit()
        
        yield Request(url=item['osize_url'], callback=self.parse_download)


    def parse_download(self, response):
        hxs = HtmlXPathSelector(response)
        #flickr_id = re.findall('/photos/\w+/(\d+)/sizes/k/in/photostream/', response.url)[0]
        download_url = hxs.select("//div[@id='allsizes-photo']/img/@src").extract()[0]

        yield Request(url=download_url, callback=self.real_download)

    def real_download(self, response):
        photo_id = re.findall('/photos/\w+/(\d+)/sizes/o/in/\w+/', response.request.headers['Referer'])[0]
        cu = self.conn.cursor()
        sql = "select photo_id, web_url, name, set_id, set_name, osize_url from photos where photo_id = %s" % photo_id
        cu.execute(sql)
        row = cu.fetchone()

        item = PhotoItem()
        item['photo_id'] = row[0]
        item['web_url'] = row[1]
        item['name'] = row[2]
        item['set_id'] = row[3]
        item['set_name'] = row[4]
        item['osize_url'] = row[5]
        item['download_url'] = response.url
        self.photo_store.save(item['name'], item['set_name'], response.body)

        return item

from os import path
import os
class PhotoStore(object):
    def __init__(self, username, basedir='.photos'):
        self.basedir = os.path.join(basedir, username)
        if not path.exists(basedir):
            os.makedirs(basedir)

    def save(self, name, set_name, body):
        if not path.exists(path.join(self.basedir, set_name)):
            os.makedirs(path.join(self.basedir, set_name))
        if not name.lower().endswith('.jpg'):
            name = name + '.jpg'
        fn = path.join(self.basedir, set_name, name)
        open(fn, 'w').write(body)

