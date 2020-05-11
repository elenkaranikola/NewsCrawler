# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item

class DogSpider(CrawlSpider):
    name = 'thetoc'
    allowed_domains = ['thetoc.gr']
    start_urls = ['https://www.thetoc.gr/']

    rules = (Rule(LinkExtractor(allow=('thetoc.gr/athlitika'), deny=('binteo','videos','gallery','eikones','twit')), callback='parseItemThetoc', follow=True), )

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
                "subtopic": "sport",
                "website": url.split('/')[2],
                "title": title,
                "date": " ".join(re.findall(r"[0-9]+.[α-ωΑ-Ω]+\..[0-9]+",response.xpath('//span[@class="article-date"]/text()').get())),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="author-social"]//h5/a/span[2]/text()').get()),
                "text": re.sub( r'\n|\t',"",text),
                "url": url,                
            }


