# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item

class DogSpider(CrawlSpider):
    name = 'amna'
    allowed_domains = ['amna.gr']
    start_urls = ['https://www.amna.gr/sport']

    rules = ( Rule(LinkExtractor(allow=('sport'),deny=()),callback='parseItemAmna', follow=True),  )

    def parseItemAmna(self,response):
        title = response.xpath('//div[@class="articleTitle"]/h1/text()').get() 
        text = response.xpath('//span[@class="ng-binding"]/p/text()').getall()
        if title is not None:
            yield {
                "text": text, #response.xpath('//div[@class="body"]/p[@align="justify"]/text()').getall(),
            }
