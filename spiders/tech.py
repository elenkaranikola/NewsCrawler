# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item

class DogSpider(CrawlSpider):
    name = 'tech'
    allowed_domains = ['cnn.gr','protagon.gr','in.gr']
    start_urls = ['https://www.cnn.gr/','https://www.protagon.gr/themata/','https://www.in.gr/tech/']

    rules = (
        Rule(LinkExtractor(allow=('cnn.gr/tech'), deny=('cnn.gr/tech/gallery/')), callback='parseItemCnn', follow=True), 
        Rule(LinkExtractor(allow=('protagon.gr/themata/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parseItemProtagon', follow=True),
        Rule(LinkExtractor(allow=(r"\.in\.gr.+/tech/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parseItemIn', follow=True), 
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
                "subtopic": "tech",
                "website": url.split('/')[2],
                "title": title,
                "date": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get()),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-author"]/text()').get()),
                "text": re.sub( r'\n|\t',"",text),
                "url": url,                
            }

    def parseItemProtagon(self,response):
        sub = response.xpath('//span[@class="s_roumpr"]/a/text()').get()
        if sub == "Επιστήμη & Τεχνολογία":
            title = response.xpath('//h1[@class="entry-title"]/text()').get() 
            text = response.xpath('//div[@class="left-single-column "]//p/text()|//div[@class="left-single-column "]//strong/text()|//div[@class="left-single-column "]//p/*/text()').getall()
            text = " ".join(" ".join(text))
            text = re.sub( "  ", "space",text)
            text = re.sub( " ", "",text)
            text = re.sub( "space", " ",text)
            text = re.sub( "\xa0","",text)
            #flag to see later on if we have tweets ect
            flag = re.search(r"@",text)
            url = response.url
            author = re.findall(r"(\w+).(\w+)",response.xpath('//strong[@class="generalbold uppercase"]/a/text()').get())
            #from list to tuple to string
            author = author[0]
            author = ' '.join(author)
            date = re.findall(r"(\d+).(\w+).(\d+)",response.xpath('//span[@class="generalight uppercase"]/text()').get())
            date = date[0]
            date = ' '.join(date)
            #check if we are in an article, and if it doesn't have images
            if title is not None and len(text)>10 and flag is None:
                yield {
                    "subtopic": sub,
                    "website": url.split('/')[2],
                    "title": title,
                    "date": date, 
                    "author": author,
                    "text": re.sub( r'\s\s\s',"",text),
                    "url": url,                
                }

    def parseItemIn(self,response):
        title = response.xpath('//h1[@class="entry-title black-c"]/text()').get() 
        text = response.xpath('//div[@class="main-content pos-rel article-wrapper"]//p/text()|//div[@class="main-content pos-rel article-wrapper"]//strong/text()|//div[@class="main-content pos-rel article-wrapper"]//p/*/text()').getall()
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
                "subtopic": "tech",
                "website": url.split('/')[2],
                "title": title,
                "date": response.xpath('//time/text()').get(), 
                "author": response.xpath('//span[@class="vcard author"]//a/text()').get(),
                "text": re.sub( r'\s\s\s',"",text),
                "url": url,                
            }


