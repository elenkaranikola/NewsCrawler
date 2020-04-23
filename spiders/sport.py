# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item


class SportSpider(CrawlSpider):
    name = 'sport'
    allowed_domains = ['gazzetta.gr','sport24.gr','cnn.gr','reader.gr']
    start_urls = ['http://www.gazzetta.gr/','https://www.sport24.gr','https://www.cnn.gr','https://www.reader.gr/athlitismos']

    rules = (
            Rule(LinkExtractor(allow=('gazzetta.gr/football/','gazzetta.gr/basketball/','gazzetta.gr/other-sports/','gazzetta.gr/volleyball/','gazzetta.gr/tennis/'), 
            deny=('power-rankings/','vid','gallery','pic')),callback='parseItemGazzetta', follow=True),    
            Rule(LinkExtractor(allow=('sport24.gr/football/','sport24.gr/sports/','sport24.gr/Basket/'), 
            deny=('vid','gallery','pic')),callback='parseItemSport24', follow=True),
            Rule(LinkExtractor(allow=('cnn.gr/news/sports')),callback='parseItemCnn', follow=True),
            Rule(LinkExtractor(allow=('reader.gr/athlitismos'), deny=('vid')), callback='parseReaderCrawl', follow=True),
             )

    
    #function for times from sport24
    def parseItemSport24(self,response):
        title = response.xpath('//div[@class="storyContent"]/h1/text()').get()
        #text = response.xpath('//div[@class="body"]/p[@align="justify"]/text()').getall()
        text = response.xpath('//div[@itemprop="articleBody"]//p/text()|//div[@itemprop="articleBody"]//h3/text()|//div[@itemprop="articleBody"]//p/*/text()').getall()
        #text = type(text)
        text = " ".join(" ".join(text))
        text = re.sub( "  ", "space",text)
        text = re.sub( " ", "",text)
        text = re.sub( "space", " ",text)
        text = re.sub(r'\n|\t',"",text)
        url = response.url
        subtopic = url.split('/')[3]
        website = url.split('/')[2]
        if title is not None:
            yield {
                "subtopic": subtopic,
                "website" : website,
                "title": title,
                "date": response.xpath('//span[@class="byline_date"]/b/text()').get(),
                "author": response.xpath('//span[@class="byline_author"]/b/text()').get(),
                "text": text, 
                "url": url
            }

    #function for items from gazzetta
    def parseItemGazzetta(self, response):
        title = response.xpath('//div[@class="field-item even"]/h1/text()').get()
        url = response.url
        # extract subtitle by splitting our url by '/'
        # and keeping the third object on our created list
        subtopic = url.split('/')[3]
        website = url.split('/')[2]
        temp=response.xpath('//span[@itemprop="name"]/text()').get()
        #elegxos an fernoume ontws ton sugrafea
        #dioti se merika artha h thesh toy allazei
        if isinstance(temp,str):
            author = re.fullmatch(r'\W+',temp)
            if author is None:
                author = temp
            else:
                author = "Unknown"
        else:
            author = response.xpath('//h3[@class="blogger-social"]/a/text()').get()
        #check if our title traces from an article url in the website
        if title is not None:
            yield {
                "subtopic": subtopic,
                "website": website,
                "title": title,
                "date": response.xpath('//div[@class="article_date"]/text()').get(),
                "author": author,
                "text": response.xpath('//div[@itemprop="articleBody"]//p/text()|//p/a/text()|//p/strong/text()').getall() ,#|//div[@itemprop="articleBody"]//p/a/text()|div[@itemprop="articleBody"]//p/strong/text()').getall(),
                "url": url
            }
#function for cnn crawl
    def parseItemCnn(self,response):
        title = response.xpath('//h1[@class="story-title"]/text()').get() 
        text = response.xpath('//p/text()').getall()
        text = " ".join(" ".join(text))
        text = re.sub( "  ", "space",text)
        text = re.sub( " ", "",text)
        text = re.sub( "space", " ",text)
        url = response.url
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
#the next two functions needed to crawl reader.gr
    def parseReaderCrawl(self,response):
        links = response.xpath('//h1[@class="article-title"]/a/@href|//div[@class="row region"]').getall()
        for link in links:
            if len(link) < 100:
                url = response.urljoin(link)
                yield Request(url,callback=self.parseItemReader)


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
                "subtopic": "sport",
                "website": url.split('/')[2],
                "title": re.sub( r'\n|\t',"",title),
                "date": re.sub( r'\n|\t',"",response.xpath('//time/text()').get()),
                "author": author,
                "text": re.sub( r'\n|\t',"",text),
                "url": url,              
            }






    


