# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item

class DogSpider(CrawlSpider):
    name = 'style'
    allowed_domains = ['cnn.gr']
    start_urls = ['cnn.gr/style/moda']
    ...

    def parse(self, response):
        pages =  180
        for page in range(2, pages, 9):
            url = 'https://www.cnn.gr/style/moda?start={}'.format(page)
            yield Request(url, callback = self.parseItemCnn, dont_filter=False)
    

    def parseItemCnn(self,response):
        url = response.xpath('//a[@href]')
        yield Request(url, callback = self.ParseItem, dont_filter=False)

    def ParseItem(self,response):
        title = response.xpath('//h1/text()')
        yield {
            "title":title,
        }



