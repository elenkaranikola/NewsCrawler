# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item

class DogSpider(CrawlSpider):
    name = 'greece'
    allowed_domains = ['cnn.gr']
    start_urls = ['https://www.cnn.gr/']

    rules = (Rule(LinkExtractor(allow=('cnn.gr/news/ellada'), deny=('cnn.gr/news/ellada/gallery/')), callback='parseItemCnn', follow=True), )

    def parseItemCnn(self,response):
        title = response.xpath('//h1[@class="story-title"]/text()').get() 
        #title = re.sub( r'\n|\t',"",title)
        text = response.xpath('//div[@class="story-content"]//p/*/text()|//div[@class="story-content"]//p/text()|//div[@class="story-content"]//p/a/*/text()').getall()
        text = " ".join(" ".join(text))
        text = re.sub( "  ", "space",text)
        text = re.sub( " ", "",text)
        text = re.sub( "space", " ",text)
        text = re.sub( "\xa0","",text)
        url = response.url
        if title is not None:
            yield {
                "subtopic": "greece",
                "website": url.split('/')[2],
                "title": title,
                "date": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get()),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-author"]/text()').get()),
                "text": re.sub( r'\n|\t',"",text),
                "url": url,                
            }
