# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item

class DogSpider(CrawlSpider):
    name = 'cnn'
    allowed_domains = ['cnn.gr']
    start_urls = ['https://www.cnn.gr/news/sports']

    rules = ( Rule(LinkExtractor(allow=('cnn.gr/news/sports'),deny=()),callback='parseItemCnn', follow=True),  )

    def parseItemCnn(self,response):
        title = response.xpath('//h1[@class="story-title"]/text()').get() 
        url = response.url
        if title is not None:
            yield {
                "subtopic": "sports",
                "website": url.split('/')[2],
                "title": title,
                "date": response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get(),
                "author": response.xpath('//div[@class="story-author"]/text()').get(),
                "text": response.xpath('//div[@class="story-text story-fulltext"]/p/text()').getall(),
                "url": url,                
            }
