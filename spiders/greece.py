# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item

class DogSpider(CrawlSpider):
    name = 'greece'
    allowed_domains = ['cnn.gr',
                    'reader.gr',
                    'thetoc.gr',
                    'protagon.gr',
                    ]
    start_urls = [
                'https://www.cnn.gr/',
                'https://www.reader.gr/news/koinonia',
                'https://www.thetoc.gr/',
                'https://www.protagon.gr/epikairotita/ellada',
                ]

    rules = (
        Rule(LinkExtractor(allow=('thetoc.gr/koinwnia')), callback='parseItemThetoc', follow=True),
        Rule(LinkExtractor(allow=('cnn.gr/news/ellada'), deny=('cnn.gr/news/ellada/gallery/','protoselida')), callback='parseItemCnn', follow=True),
        Rule(LinkExtractor(allow=('reader.gr/news/koinonia'), deny=('vid')), callback='parseItemReader', follow=True), 
        Rule(LinkExtractor(allow=('protagon.gr/epikairotita/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parseItemProtagon', follow=True),

    )

    def parseItemCnn(self,response):
        title = response.xpath('//h1[@class="story-title"]/text()').get() 
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

    def parseItemReader(self,response):
        title = response.xpath('//h1/text()').get() 
        text = response.xpath('//div[@class="article-summary"]//p/text()|//div[@class="article-body"]//p/text()|//div[@class="article-body"]//p/*/text()').getall()
        text = " ".join(" ".join(text))
        text = re.sub( "  ", "space",text)
        text = re.sub( " ", "",text)
        text = re.sub( "space", " ",text)
        text = re.sub( "\xa0","",text)
        author = response.xpath('//p[@class="article-author"]/a/text()').get()
        if author is not None:
            author = re.sub("\xa0","",author)
        else:
            author = "Unknown"
        url = response.url
        if title is not None:
            yield {
                "subtopic": "society",
                "website": url.split('/')[2],
                "title": re.sub( r'\n|\t',"",title),
                "date": re.sub( r'\n|\t',"",response.xpath('//time/text()').get()),
                "author": author,
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
        url = response.url
        if title is not None and len(text)>10:
            yield {
                "subtopic": "society",
                "website": url.split('/')[2],
                "title": title,
                "date": " ".join(re.findall(r"[0-9]+.[α-ωΑ-Ω]+\..[0-9]+",response.xpath('//span[@class="article-date"]/text()').get())),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="author-social"]//h5/a/span[2]/text()').get()),
                "text": re.sub( r'\n|\t',"",text),
                "url": url,                
            }

    def parseItemProtagon(self,response):
        sub = response.xpath('//span[@class="s_roumpr"]/a/text()').get()
        if sub == "Ελλάδα":
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