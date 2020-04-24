# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item

class DogSpider(CrawlSpider):
    name = 'economics'
    allowed_domains = [
        'cnn.gr',
        'reader.gr',
        'thetoc.gr',
        'protagon.gr',
        'periodista.gr',
        'in.gr',
        ]
    start_urls = [
        'https://www.cnn.gr/',
        'https://www.reader.gr/news/oikonomia',
        'https://www.thetoc.gr/',
        'https://www.protagon.gr/epikairotita/',
        'http://www.periodista.gr/oikonomia',
        'https://www.in.gr/economy/'
        ]

    rules = (
        Rule(LinkExtractor(allow=('periodista.gr/oikonomia'), deny=()), callback='parseInfinitePeriodista', follow=True),
        Rule(LinkExtractor(allow=('cnn.gr/oikonomia'), deny=('cnn.gr/oikonomia/gallery/')), callback='parseItemCnn', follow=True), 
        Rule(LinkExtractor(allow=('reader.gr/news/oikonomia'), deny=('vid')), callback='parseItemReader', follow=True),
        Rule(LinkExtractor(allow=('thetoc.gr/oikonomia'), deny=('binteo','videos','gallery','eikones','twit')), callback='parseItemThetoc', follow=True),
        Rule(LinkExtractor(allow=('protagon.gr/epikairotita/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parseItemProtagon', follow=True),
        Rule(LinkExtractor(allow=(r"\.in\.gr.+/economy/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parseItemIn', follow=True), 
        )

    def parseItemCnn(self,response):
        title = response.xpath('//h1[@class="story-title"]/text()').get() 
        text = response.xpath('//div[@class="story-content"]//p/text()|//div[@class="story-content"]//strong/text()|//div[@class="story-content"]//a/text()').getall()
        text = " ".join(" ".join(text))
        text = re.sub( "  ", "space",text)
        text = re.sub( " ", "",text)
        text = re.sub( "space", " ",text)
        text = re.sub( "\xa0","",text)
        url = response.url
        if title is not None and len(text)>10:
            yield {
                "subtopic": url.split('/')[4],
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
                "subtopic": "economics",
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
                "subtopic": "economics",
                "website": url.split('/')[2],
                "title": title,
                "date": " ".join(re.findall(r"[0-9]+.[α-ωΑ-Ω]+\..[0-9]+",response.xpath('//span[@class="article-date"]/text()').get())),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="author-social"]//h5/a/span[2]/text()').get()),
                "text": re.sub( r'\n|\t',"",text),
                "url": url,                
            }

    def parseItemProtagon(self,response):
        sub = response.xpath('//span[@class="s_roumpr"]/a/text()').get()
        if sub == "Οικονομία":
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
    #next 3 function for periodista.gr webcrawling
    def parseInfinitePeriodista(self,response):
        pages =  630
        for page in range(0 ,pages , 30):
            url = 'http://www.periodista.gr/oikonomia?start={}'.format(page)
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
                "subtopic": "Οικονομία",
                "website": url.split('/')[2],
                "title": re.sub( r'\t|\n|\r',"",title),
                "date": re.sub(r'\t|\n|\r',"",response.xpath('//div[@class="col-md-4 per-color-grey per-font-size-md per-padding-top-20"]/text()').get()), 
                "author": "Δημήτρη Μπεκιάρη",
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
                "subtopic": "Οικονομικά",
                "website": url.split('/')[2],
                "title": title,
                "date": response.xpath('//time/text()').get(), 
                "author": response.xpath('//span[@class="vcard author"]//a/text()').get(),
                "text": re.sub( r'\s\s\s',"",text),
                "url": url,                
            }
