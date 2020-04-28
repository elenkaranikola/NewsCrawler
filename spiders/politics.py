# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item
from news2.settings import PERIODISTA_VARS

class DogSpider(CrawlSpider):
    name = 'politics'
    allowed_domains = [
        'cnn.gr',
        'reader.gr',
        'thetoc.gr',
        'protagon.gr',
        'periodista.gr',
        'in.gr',
        'newpost.gr',
        ]
    url = [
        'https://www.cnn.gr/',
        'https://www.reader.gr',
        'https://www.thetoc.gr/',
        'https://www.protagon.gr/epikairotita/',
        'https://www.in.gr/politics/',
        'http://www.periodista.gr/',
        'http://newpost.gr/'
        ]
    urls = url + ['http://www.periodista.gr/politiki?start={}'.format(x) for x in range(1,PERIODISTA_VARS['POLITICS_PAGES'],30)]+['http://newpost.gr/politiki?page={}'.format(x) for x in range(1,13147)] 
    #urls_with_periodista = urls + ['http://www.periodista.gr/politiki?start={}'.format(x) for x in range(1,PERIODISTA_VARS['ECONOMY_PAGES'])]
    start_urls = urls[:]

    rules = (
        Rule(LinkExtractor(allow=('cnn.gr/news/politiki'), deny=('cnn.gr/news/politiki/gallery/','protoselida')), callback='parseItemCnn', follow=True),
        Rule(LinkExtractor(allow=('reader.gr/news/politiki'), deny=('vid')), callback='parseItemReader', follow=True), 
        Rule(LinkExtractor(allow=('thetoc.gr/politiki'), deny=('binteo','videos','gallery','eikones','twit')), callback='parseItemThetoc', follow=True),
        Rule(LinkExtractor(allow=('protagon.gr/epikairotita/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parseItemProtagon', follow=True),
        Rule(LinkExtractor(allow=('periodista.gr/politiki'), deny=()), callback='parse_periodista', follow=True),   
        Rule(LinkExtractor(allow=(r"\.in\.gr.+/politics/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parseItemIn', follow=True), 
        Rule(LinkExtractor(allow=('newpost.gr/politiki'), deny=()), callback='parse_newpost', follow=True),
    )

    def parseItemCnn(self,response):
        title = response.xpath('//h1[@class="story-title"]/text()').get() 
        text = response.xpath('//div[@class="story-content"]//p/text()|//div[@class="story-content"]//strong/text()|//div[@class="story-content"]//a/text()').getall()
        listtostring = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",listtostring)
        uneededspaces = re.sub( " ", "",markspaces)
        finaltext = re.sub( "space", " ",uneededspaces)
        clearcharacters = re.sub( "\xa0","",finaltext)
        url = response.url
        if title is not None and len(clearcharacters)>10:
            yield {
                "subtopic": "Politics",
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": title,
                "date": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get()),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-author"]/text()').get()),
                "text": re.sub( r'\n|\t',"",clearcharacters),
                "url": url,                
            }

    def parseItemReader(self,response):
        title = response.xpath('//h1/text()').get() 
        text = response.xpath('//div[@class="article-summary"]//p/text()|//div[@class="article-body"]//p/text()|//div[@class="article-body"]//p/*/text()').getall()
        listtostring = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",listtostring)
        uneededspaces = re.sub( " ", "",markspaces)
        finaltext = re.sub( "space", " ",uneededspaces)
        clearcharacters = re.sub( "\xa0","",finaltext)
        author = response.xpath('//p[@class="article-author"]/a/text()').get()
        if author is not None:
            author = re.sub("\xa0","",author)
        else:
            author = "reader.gr"
        url = response.url
        if title is not None:
            yield {
                "subtopic": "Politics",
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": re.sub( r'\n|\t',"",title),
                "date": re.sub( r'\n|\t',"",response.xpath('//time/text()').get()),
                "author": author,
                "text": re.sub( r'\n|\t',"",clearcharacters),
                "url": url,              
            }

    def parseItemThetoc(self,response):
        title = response.xpath('//div[@class="article-title"]//h1/text()').get() 
        text = response.xpath('//div[@class="article-content articleText"]//p/text()|//div[@class="article-content articleText"]//strong/text()|//div[@class="article-content articleText"]//p/*/text()').getall()
        listtostring = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",listtostring)
        uneededspaces = re.sub( " ", "",markspaces)
        finaltext = re.sub( "space", " ",uneededspaces)
        clearcharacters = re.sub( "\xa0","",finaltext)
        url = response.url
        if title is not None and len(clearcharacters)>10:
            yield {
                "subtopic": url.split('/')[3],
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": title,
                "date": " ".join(re.findall(r"[0-9]+.[α-ωΑ-Ω]+\..[0-9]+",response.xpath('//span[@class="article-date"]/text()').get())),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="author-social"]//h5/a/span[2]/text()').get()),
                "text": re.sub( r'\n|\t',"",clearcharacters),
                "url": url,                
            }

    def parseItemProtagon(self,response):
        sub = response.xpath('//span[@class="s_roumpr"]/a/text()').get()
        if sub == "Πολιτική":
            title = response.xpath('//h1[@class="entry-title"]/text()').get() 
            text = response.xpath('//div[@class="left-single-column "]//p/text()|//div[@class="left-single-column "]//strong/text()|//div[@class="left-single-column "]//p/*/text()').getall()
            listtostring = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",listtostring)
            uneededspaces = re.sub( " ", "",markspaces)
            finaltext = re.sub( "space", " ",uneededspaces)
            clearcharacters = re.sub( "\xa0","",finaltext)
            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clearcharacters)
            url = response.url
            author = re.findall(r"(\w+).(\w+)",response.xpath('//strong[@class="generalbold uppercase"]/a/text()').get())
            #from list to tuple to string
            listtotuple = author[0]
            author = ' '.join(listtotuple)
            date = re.findall(r"(\d+).(\w+).(\d+)",response.xpath('//span[@class="generalight uppercase"]/text()').get())
            listtotuple = date[0]
            date = ' '.join(listtotuple)
            #check if we are in an article, and if it doesn't have images
            if title is not None and len(clearcharacters)>10 and flag is None:
                yield {
                    "subtopic": "Politics",
                    "website": re.search(r"www.+\.gr",url).group(0),
                    "title": title,
                    "date": date, 
                    "author": author,
                    "text": re.sub( r'\s\s\s',"",clearcharacters),
                    "url": url,                
                }
        else: 
            pass

    def parse_periodista(self,response):
        title = response.xpath('//h1[@itemprop="headline"]/text()').get() 
        text = response.xpath('//div[@class="per-item-page-part per-article-body"]//p/text()|//div[@class="per-item-page-part per-article-body"]//strong/text()|//div[@class="per-item-page-part per-article-body"]//p/*/text()').getall()
        list_to_string = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        final_text = re.sub( "space", " ",uneeded_spaces)
        clear_characters = re.sub( "\xa0","",final_text)
        url = response.url
        #flag to see later on if we have videos
        flag = re.search(r"binteo|foto",url)
        #check if we are in an article, and if it doesn't have videos
        if title is not None and len(clear_characters)>10 and flag is None:
            yield {
                "subtopic": "Politics",
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": re.sub( r'\t|\n|\r',"",title),
                "date": re.sub(r'\t|\n|\r',"",response.xpath('//div[@class="col-md-4 per-color-grey per-font-size-md per-padding-top-20"]/text()').get()), 
                "author": "periodista.gr",
                "text": re.sub( r'\s\s\s',"",clear_characters),
                "url": url,                
            }  

    def parseItemIn(self,response):
        title = response.xpath('//h1[@class="entry-title black-c"]/text()').get() 
        text = response.xpath('//div[@class="main-content pos-rel article-wrapper"]//p/text()|//div[@class="main-content pos-rel article-wrapper"]//strong/text()|//div[@class="main-content pos-rel article-wrapper"]//p/*/text()').getall()
        listtostring = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",listtostring)
        uneededspaces = re.sub( " ", "",markspaces)
        finaltext = re.sub( "space", " ",uneededspaces)
        clearcharacters = re.sub( "\xa0","",finaltext)
        #flag to see later on if we have tweets ect
        flag = re.search(r"@",clearcharacters)
        url = response.url
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(text)>10 and flag is None:
            yield {
                "subtopic": "Politics",
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": title,
                "date": response.xpath('//time/text()').get(), 
                "author": response.xpath('//span[@class="vcard author"]//a/text()').get(),
                "text": re.sub( r'\s\s\s',"",clearcharacters),
                "url": url,                
            }

    def parse_newpost(self,response):
        title = response.xpath('//h1[@class="article-title"]/text()').get() 
        text = response.xpath('//div[@class="article-main clearfix"]//p/text()|//div[@class="article-main clearfix"]//strong/text()|//div[@class="article-main clearfix"]//p/*/text()').getall()
        list_to_string = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        final_text = re.sub( "space", " ",uneeded_spaces)
        clear_characters = re.sub( "\xa0","",final_text)
        #flag to see later on if we have tweets ect
        flag = re.search(r"@",clear_characters)
        url = response.url
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(clear_characters)>10 and flag is None:
            yield {
                "subtopic": "Politics",
                "website": "newpost.gr",
                "title": title,
                "date": (response.xpath('//small[@class="article-created-time"]/text()').get()).split('/')[0], 
                "author": "newpost.gr",
                "text": re.sub( r'\s\s\s',"",clear_characters),
                "url": url,                
        }


