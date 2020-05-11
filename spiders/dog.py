# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item


class DogSpider(CrawlSpider):
    name = 'dog'
    allowed_domains = ['sportdog.gr']
    start_urls = ['https://sportdog.gr/']

    rules = (Rule(LinkExtractor(allow=('sportdog.gr/category/sports/podosfairo','sportdog.gr/category/sports/mpasket','sportdog.gr/category/sports/alla-spor'),
             deny=()),callback='parseItemSportdog', follow=True),  )

    def parseItemSportdog(self, response):
        title = response.xpath('//div[@class="container"]/h1/text()').get() 
        text = response.xpath('//div[@class="art-body"]/p/text()').getall()
        if title is not None:
            yield {
                "text": text, #response.xpath('//div[@class="body"]/p[@align="justify"]/text()').getall(),
            }
