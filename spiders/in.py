# -*- coding: utf-8 -*-
import scrapy


class InSpider(scrapy.Spider):
    name = 'in'
    allowed_domains = ['in.gr']
    start_urls = ['http://in.gr/']

    def parse(self, response):
        pass
