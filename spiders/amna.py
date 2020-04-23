# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item


class GazSpider(CrawlSpider):
    handle_httpstatus_list = [301]
    name = 'amna'
    allowed_domains = ['amna.gr']
    start_urls = ['http://amna.gr/sport/']

    rules = [Rule(LinkExtractor(allow=('/sport/article'), deny=()), callback='parseItemAmna', follow=True, ), ]
    
    #function for items from gazzetta
    def parseItemAmna(self, response):
        title = response.xpath('//div[@class="articleTitle"]/h1/text()').get()
        if title is not None:
            yield {
                "title": title,
            }
