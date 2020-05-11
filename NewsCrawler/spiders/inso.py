# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item
from news2.settings import LIFO_VARS

class DogSpider(CrawlSpider):
    name = 'inso'
    allowed_domains = ['insomnia.gr']
    start_urls = ['https://www.insomnia.gr/classifieds/category/16-macbook-imac']

    rules = (
        Rule(LinkExtractor(allow=(r'www\.insomnia\.gr.+classifieds/item'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_insomnia', follow=True), 
        )

    def parse_insomnia(self,response):
        price = response.xpath('//div[@class="price grid__col-auto grid--justify-center"]/p/text()').get()
        price = re.search(r'\d*\.*\d*,\d*',price).group(0)
        yield {
            "text": price,
            "url": response.url,                
        }
