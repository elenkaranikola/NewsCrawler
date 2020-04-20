# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item


class SportSpider(CrawlSpider):
    name = 'sport'
    allowed_domains = ['gazzetta.gr','sport24.gr','sportdog.gr','amna.gr']
    start_urls = ['http://www.gazzetta.gr/','https://www.sport24.gr','https://www.sportdog.gr','https://www.amna.gr/sport/']
    #base_url = 'http://www.gazzetta.gr/'


    #rules refering to gazzetta.gr
    #rules = (Rule(LinkExtractor(allow=('football/','/basketball/','/other-sports/','/volleyball/','tennis/'), deny=('power-rankings/','sport24')),callback='parseItemGazzetta', follow=True),    
    #        Rule(LinkExtractor(allow=('football/','/sports/','/Basket/'), deny=('gazzetta')),callback='parseItemSport24', follow=True), )
        #Rule(LinkExtractor(allow=('football/','/basketball/','/other-sports/','/voleyball/','/tennis/'), deny=('power-rankings/'), allow_domains=('gazzetta.gr/') ),callback='parseItemGazzetta', follow=True), )
    rules = (Rule(LinkExtractor(allow=('gazzetta.gr/football/','gazzetta.gr/basketball/','gazzetta.gr/other-sports/','gazzetta.gr/volleyball/','gazzetta.gr/tennis/'), 
            deny=('power-rankings/')),callback='parseItemGazzetta', follow=True),    
            Rule(LinkExtractor(allow=('sport24.gr/football/','sport24.gr/sports/','sport24.gr/Basket/'), 
            deny=()),callback='parseItemSport24', follow=True),
            Rule(LinkExtractor(allow=('sportdog.gr/category/sports/podosfairo','sportdog.gr/category/sports/mpasket','sportdog.gr/category/sports/alla-spor'), 
            deny=()),callback='parseItemSportdog', follow=True),
            Rule(LinkExtractor(allow=('amna.gr/sport/'), deny=()),callback='parseItemAmna', follow=True), 
            )

    
    #function for times from sport24
    def parseItemSport24(self,response):
        title = response.xpath('//div[@class="storyContent"]/h1/text()').get()
        text = response.xpath('//div[@class="body"]/p[@align="justify"]/text()').getall()
        #text = type(text)
        text = " ".join(" ".join(text))
        text = re.sub( "  ", "!ElENH!",text)
        text = re.sub( " ", "",text)
        text = re.sub( "!ElENH!", " ",text)
        url = response.url
        subtopic = url.split('/')[3]
        website = url.split('/')[2]
        if title is not None:
            yield {
                "subtopic": subtopic,
                "website" : website,
                "title": title,
                "date": response.xpath('//span[@class="byline_date"]/b/text()').get(),
                "author": response.xpath('//span[@class="byline_author"]/b/text()').get(),
                "text": text, 
                "url": url
            }

    def parseItemSportdog(self,response):
        yield {}

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
                "url": url
            }
        
    def parseItemAmna(self, response):
        title = response.xpath('//div[@class="articleTttle"]/h1/text()').get() 
        text = response.xpath('//span[@class="ng-binding"]/p/text()').getall()
        if title is not None:
            yield {
                "text": text, #response.xpath('//div[@class="body"]/p[@align="justify"]/text()').getall(),
            }






    


