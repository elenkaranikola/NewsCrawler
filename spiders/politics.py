# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item

class DogSpider(CrawlSpider):
    name = 'politics'
    allowed_domains = ['cnn.gr','reader.gr']
    start_urls = ['https://www.cnn.gr/','https://www.reader.gr']

    rules = (
        Rule(LinkExtractor(allow=('cnn.gr/news/politiki'), deny=('cnn.gr/news/politiki/gallery/')), callback='parseItemCnn', follow=True),
        Rule(LinkExtractor(allow=('reader.gr/news/politiki'), deny=('')), callback='parseItemReader', follow=True), 
    )

    def parseItemCnn(self,response):
        title = response.xpath('//h1[@class="story-title"]/text()').get() 
        #title = re.sub( r'\n|\t',"",title)
        text = response.xpath('//div[@class="story-content"]//p/text()|//div[@class="story-content"]//strong/text()|//div[@class="story-content"]//a/text()').getall()
        text = " ".join(" ".join(text))
        text = re.sub( "  ", "space",text)
        text = re.sub( " ", "",text)
        text = re.sub( "space", " ",text)
        text = re.sub( "\xa0","",text)
        url = response.url
        if title is not None and len(text)>10:
            yield {
                "subtopic": "world",
                "website": url.split('/')[2],
                "title": title,
                "date": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get()),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-author"]/text()').get()),
                "text": re.sub( r'\n|\t',"",text),
                "url": url,                
            }

    def parseItemReader(self,response):
        title = response.xpath('//h1[@class="story-title"]/text()').get() 
        #title = re.sub( r'\n|\t',"",title)
        text = response.xpath('//div[@class="story-content"]//p/text()|//div[@class="story-content"]//strong/text()|//div[@class="story-content"]//a/text()').getall()
        text = " ".join(" ".join(text))
        text = re.sub( "  ", "space",text)
        text = re.sub( " ", "",text)
        text = re.sub( "space", " ",text)
        text = re.sub( "\xa0","",text)
        url = response.url
        if title is not None and len(text)>10:
            yield {
                "subtopic": "world",
                "website": url.split('/')[2],
                "title": title,
                "date": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get()),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-author"]/text()').get()),
                "text": re.sub( r'\n|\t',"",text),
                "url": url,                
            }


