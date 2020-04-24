# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item

class DogSpider(CrawlSpider):
    name = 'periodista'
    allowed_domains = ['periodista.gr']
    start_urls = ['http://www.periodista.gr/']

    rules = (
        Rule(LinkExtractor(allow=('periodista.gr/kosmos'), deny=()), callback='parseInfinitePeriodista', follow=True), 
        )

    def parseInfinitePeriodista(self,response):
        pages =  1010
        for page in range(0 ,pages , 10):
            url = 'http://www.periodista.gr/kosmos?start={}'.format(page)
            yield Request(url, callback = self.parseItemPeriodista) 

    def parseItemPeriodista(self,response):
        links = response.xpath('//h2[@itemprop="headline"]/a/@href').getall()
        for link in links:
            url = response.urljoin(link)
            yield Request(url,callback=self.parseItem) 

            
    def parseItem(self,response):
        title = response.xpath('//h1[@itemprop="headline"]/text()').get() 
        text = response.xpath('//div[@class="per-item-page-part per-article-body"]//p/text()|//div[@class="per-item-page-part per-article-body"]//strong/text()|//div[@class="per-item-page-part per-article-body"]//p/*/text()').getall()
        text = " ".join(" ".join(text))
        text = re.sub( "  ", "space",text)
        text = re.sub( " ", "",text)
        text = re.sub( "space", " ",text)
        text = re.sub( "\xa0","",text)
        url = response.url
        #flag to see later on if we have videos
        flag = re.search(r"binteo|foto",url)
        #check if we are in an article, and if it doesn't have videos
        if title is not None and len(text)>10 and flag is None:
            yield {
                "subtopic": "Κόσμος",
                "website": url.split('/')[2],
                "title": re.sub( r'\t|\n|\r',"",title),
                "date": re.sub(r'\t|\n|\r',"",response.xpath('//div[@class="col-md-4 per-color-grey per-font-size-md per-padding-top-20"]/text()').get()), 
                "author": "Δημήτρη Μπεκιάρη",
                "text": re.sub( r'\s\s\s',"",text),
                "url": url,                
            }
