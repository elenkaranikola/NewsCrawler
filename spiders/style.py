# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item

class DogSpider(CrawlSpider):
    name = 'style'
    allowed_domains = ['cnn.gr','thetoc.gr']
    start_urls = ['https://www.cnn.gr/style/politismos','https://www.thetoc.gr/']

    rules = (
        Rule(LinkExtractor(allow=('/politismos/'),deny=('gallery')), callback='parseInfiniteCnn', follow=True), 
        Rule(LinkExtractor(allow=('thetoc.gr/people-style'), deny=('binteo','videos','gallery','eikones','twit')), callback='parseItemThetoc', follow=True),
        )

#next three functions for cnn infinite scroll for fashion
    def parseInfiniteCnn(self,response):
        pages =  180
        for page in range(0, pages ,9):
            url = 'https://www.cnn.gr/style/moda?start={}'.format(page)
            yield Request(url, callback = self.parseItemCnn) 

    def parseItemCnn(self,response):
        links = response.xpath('//h3[@class="item-title"]/a/@href').getall()
        for link in links:
            url = response.urljoin(link)
            yield Request(url,callback=self.parseItem) #"url": response.urljoin(link),

            
    def parseItem(self,response):
        text = response.xpath('//div[@class="story-content"]//p/text()|//div[@class="story-content"]//strong/text()|//div[@class="story-content"]//a/text()').getall()
        title = response.xpath('//h1[@class="story-title"]/text()').get()
        text = " ".join(" ".join(text))
        text = re.sub( "  ", "space",text)
        text = re.sub( " ", "",text)
        text = re.sub( "space", " ",text)
        url = response.url
        article_type = url.split('/')[5]
        contains_photos = re.search('Photos',text)
        if article_type == "story" and contains_photos is None:
            yield{ 
                "subtopic": "moda",
                "website": url.split('/')[2],
                "title": title,
                "date": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get()),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-author"]/text()').get()),
                "text": re.sub( r'\n|\t',"",text),
                "url": url,     
            }

    def parseItemThetoc(self,response):
        title = response.xpath('//div[@class="article-title"]//h1/text()').get() 
        text = response.xpath('//div[@class="article-content articleText"]//p/text()|//div[@class="article-content articleText"]//strong/text()|//div[@class="article-content articleText"]//p/*/text()').getall()
        text = " ".join(" ".join(text))
        text = re.sub( "  ", "space",text)
        text = re.sub( " ", "",text)
        text = re.sub( "space", " ",text)
        text = re.sub( "\xa0","",text)
        flag = re.search(r"@",text)
        url = response.url
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(text)>10 and flag is None:
            yield {
                "subtopic": "style",
                "website": url.split('/')[2],
                "title": title,
                "date": " ".join(re.findall(r"[0-9]+.[α-ωΑ-Ω]+\..[0-9]+",response.xpath('//span[@class="article-date"]/text()').get())),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="author-social"]//h5/a/span[2]/text()').get()),
                "text": re.sub( r'\n|\t',"",text),
                "url": url,                
            }