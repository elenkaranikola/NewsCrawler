# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item


class SportSpider(CrawlSpider):
    name = 'spo'
    allowed_domains = ['gazzetta.gr','sport24.gr']
    start_urls = ['http://www.gazzetta.gr/','https://www.sport24.gr']
    #base_url = 'http://www.gazzetta.gr/'


    #rules refering to gazzetta.gr
    rules = (
            Rule(LinkExtractor(allow=('football/','/sports/','/Basket/'), deny=('gazzetta')),callback='parseItemSport24', follow=True), 
    )

    #function for times from sport24
    def parseItemSport24(self,response):
        title = response.xpath('//div[@class="storyContent"]/h1/text()').get()
        text = response.xpath('//div[@class="body"]/p[@align="justify"]/text()').getall()
        text = " ".join(" ".join(text))
        if len(text) < 10 :
            text = response.xpath('//div[@class="storyContent"]/div/p/text()').getall()
            text = " ".join(" ".join(text))
        #text = type(text)
        text = re.sub( "  ", "space",text)
        text = re.sub( " ", "",text)
        text = re.sub( "space", " ",text)
        text = re.sub( r'\t+',r'',text)
        url = response.url
        subtopic = url.split('/')[3]
        website = url.split('/')[2]
        if title is not None:
            yield {
                "subtitle": subtopic,
                "website" : website,
                "title": title,
                "date": response.xpath('//span[@class="byline_date"]/b/text()').get(),
                "author": response.xpath('//span[@class="byline_author"]/b/text()').get(),
                "text": text, #response.xpath('//div[@class="body"]/p[@align="justify"]/text()').getall(),
                "url": url
            }

