# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item

class DogSpider(CrawlSpider):
    name = 'food'
    allowed_domains = [
        'newpost.gr'
        ]
    url = [
    'http://newpost.gr/gefsi'
    ]
    urls = ['http://newpost.gr/gefsi?page={}'.format(x) for x in range(1,1227)]
    start_urls = urls[:]  
    rules = ( 
        Rule(LinkExtractor(allow=('newpost.gr/gefsi'), deny=()), callback='parseNewpost', follow=True),   
    )
    
    def parseNewpost(self,response):
        title = response.xpath('//h1[@class="article-title"]/text()').get() 
        #text = response.xpath('//div[@class="article-main clearfix"]//strong/text()').getall()
        text = response.xpath('//div[@class="article-main clearfix"]//p/text()|//div[@class="article-main clearfix"]//li/text()|//div[@class="article-main clearfix"]//p/a/strong/text()|//div[@class="article-main clearfix"]//p/*/text()').getall()
        listtostring = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",listtostring)
        uneededspaces = re.sub( " ", "",markspaces)
        finaltext = re.sub( "space", " ",uneededspaces)
        clearcharacters = re.sub( "\xa0","",finaltext)
        #flag to see later on if we have tweets ect
        flag = re.search(r"@",clearcharacters)
        url = response.url
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(clearcharacters)>10 and flag is None:
            yield {
                "subtopic": "Food",
                "website": "newpost.gr",
                "title": title,
                "date": (response.xpath('//small[@class="article-created-time"]/text()').get()).split('/')[0], 
                "author": "Newpost.gr",
                "text": re.sub( r'\s\s\s',"",clearcharacters),
                "url": url,                
        }
