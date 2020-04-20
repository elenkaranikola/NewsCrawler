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
    start_urls = ['https://www.cnn.gr/']

    rules = (Rule(LinkExtractor(allow=('cnn.gr/news/sports')), callback='parseItemCnn', follow=True), )

    def parseItemCnn(self,response):
        title = response.xpath('//h1[@class="story-title"]/text()').get() 
        #title = re.sub( r'\n|\t',"",title)
        text = response.xpath('//p/text()').getall()
        text = " ".join(" ".join(text))
        text = re.sub( "  ", "space",text)
        text = re.sub( " ", "",text)
        text = re.sub( "space", " ",text)
        #text = re.sub(r'\n|\t',"",text)
        url = response.url
        #date = response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get()
        #date = re.sub( r'\n|\t',"",date)
        #author = response.xpath('//div[@class="story-author"]/text()').get()
        #author = re.sub(r'\n|\t',"",author)
        if title is not None:
            yield {
                "subtopic": "sports",
                "website": url.split('/')[2],
                "title": title,
                "date": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get()),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-author"]/text()').get()),
                "text": re.sub( r'\n',"",text),
                "url": url,                
            }
