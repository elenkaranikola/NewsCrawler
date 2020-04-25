# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item

class DogSpider(CrawlSpider):
    name = 'newpost'
    allowed_domains = ['newpost.gr']
    start_urls = ['http://newpost.gr/']

    rules = (
        Rule(LinkExtractor(allow=('newpost.gr/kosmos'), deny=()), callback='parseInfiniteNewpost', follow=True), 
        )
    #next 3 functions for newpost.gr
    def parseInfiniteNewpost(self,response):
        pages =  12478
        for page in range(1 ,pages):
            url = 'http://www.newpost.gr/kosmos?page={}'.format(page)
            yield Request(url, callback = self.parseItemNewpost) 

    def parseItemNewpost(self,response):
        links = response.xpath('//h2[@class="cp-title"]/a/@href').getall()
        for link in links:
            url = response.urljoin(link)
            yield Request(url,callback=self.parseNewpost) 

            
    def parseNewpost(self,response):
        title = response.xpath('//h1[@class="article-title"]/text()').get() 
        text = response.xpath('//div[@class="article-main clearfix"]//p/text()|//div[@class="article-main clearfix"]//strong/text()|//div[@class="article-main clearfix"]//p/*/text()').getall()
        text = " ".join(" ".join(text))
        text = re.sub( "  ", "space",text)
        text = re.sub( " ", "",text)
        text = re.sub( "space", " ",text)
        text = re.sub( "\xa0","",text)
        #flag to see later on if we have tweets ect
        flag = re.search(r"@",text)
        url = response.url
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(text)>10 and flag is None:
            yield {
                "subtopic": "Κόσμος",
                "website": url.split('/')[2],
                "title": title,
                "date": (response.xpath('//small[@class="article-created-time"]/text()').get()).split('/')[0], 
                "author": "Newpost.gr",
                "text": re.sub( r'\s\s\s',"",text),
                "url": url,                
           }
