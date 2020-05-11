# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item


class GazSpider(CrawlSpider):

    name = 'gaz'
    allowed_domains = ['gazzetta.gr']
    start_urls = ['http://gazzetta.gr/']

    rules = [Rule(LinkExtractor(allow=('football/','/basketball/','/other-sports/','volleyball/','tennis/'), deny=('power-rankings/')), callback='parseItemGazzetta', follow=True), ]
    
    #function for items from gazzetta
    def parseItemGazzetta(self, response):
        title = response.xpath('//div[@class="field-item even"]/h1/text()').get()
        url = response.url
        # extract subtitle by splitting our url by '/'
        # and keeping the third object on our created list
        subtopic = url.split('/')[3]
        website = url.split('/')[2]
        temp=response.xpath('//span[@itemprop="name"]/text()').get()
        #elegxos an fernoume ontws ton sugrafea
        #dioti se merika artha h thesh toy allazei
        if isinstance(temp,str):
            author = re.fullmatch(r'\W+',temp)
            if author is None:
                author = temp
            else:
                author = "Unknown"
        else:
            author = response.xpath('//h3[@class="blogger-social"]/a/text()').get()
        #check if our title traces from an article url in the website
        if title is not None:
            yield {
                "subtopic": subtopic,
                "website": website,
                "title": title,
                "date": response.xpath('//div[@class="article_date"]/text()').get(),
                "author": author, #response.xpath('//span[@itemprop="name"]/text()').get
                "text": response.xpath('//div[@itemprop="articleBody"]/p/text()').getall(),
                #"text": response.xpath('//div/div[@class="field-items"]/div[@itemprop="articleBody"]/p/text()').getall(),
                "url": url
            }
