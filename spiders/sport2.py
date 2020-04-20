# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item


class SportSpider(CrawlSpider):
    name = 'sport2'
    allowed_domains = ['gazzetta.gr','sport24.gr']
    start_urls = ['http://www.gazzetta.gr/','https://www.sport24.gr']
    #base_url = 'http://www.gazzetta.gr/'


    #rules refering to gazzetta.gr
    #rules = (Rule(LinkExtractor(allow=('football/',), deny=('power-rankings/',)),callback='parseItemGazzetta', follow=True),
     #        Rule(LinkExtractor(allow=('football/',), deny=()),callback='parseItemSport24', follow=True), ) 
    
    #LxmlLinkExtractor(allow=('football/',), deny=('power-rankings/',),callback='parseItemGazzetta')


    #function for times from sport2
    def parseItemSport24(self,response):
        print ("SPOOOOOORT")
        title = response.xpath('//div[@class="storyContent"]/h1/text()').get()
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
            }


    #function for items from gazzetta
    def parseItemGazzetta(self, response):
        print ("GAAAAAAAZEEEEEEEEEEETTAAAA")
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
            }






    


