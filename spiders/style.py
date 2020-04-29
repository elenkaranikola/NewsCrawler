# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item
from news2.settings import IEFIMERIDA_VARS

class DogSpider(CrawlSpider):
    name = 'style'
    allowed_domains = [
        'cnn.gr',
        'thetoc.gr',
        'in.gr',
        'newpost.gr',
        'iefimerida.gr',
        ]
    url = [
        'https://www.cnn.gr/style/politismos',
        'https://www.thetoc.gr/',
        'https://www.in.gr/'
        'https://newpost.gr/lifestyle',
        'https://www.iefimerida.gr',
        ]
    urls = url + ['http://newpost.gr/lifestyle?page={}'.format(x) for x in range(1,5757)]
    start_urls = urls[:]

    rules = (
        Rule(LinkExtractor(allow=('https://www.iefimerida.gr/design|https://www.iefimerida.gr/gynaika'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_iefimerida', follow=True), 
        Rule(LinkExtractor(allow=('/politismos/'),deny=('gallery')), callback='parseInfiniteCnn', follow=True), 
        Rule(LinkExtractor(allow=('thetoc.gr/people-style'), deny=('binteo','videos','gallery','eikones','twit')), callback='parseItemThetoc', follow=True),
        Rule(LinkExtractor(allow=(r"\.in\.gr.+/health/|\.in\.gr.+/life/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parseItemIn', follow=True),
        Rule(LinkExtractor(allow=('newpost.gr/lifestyle'), deny=()), callback='parseNewpost', follow=True), 
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
        listtostring = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",listtostring)
        uneededspaces = re.sub( " ", "",markspaces)
        finaltext = re.sub( "space", " ",uneededspaces)
        url = response.url
        article_type = url.split('/')[5]
        contains_photos = re.search('Photos',finaltext)
        if article_type == "story" and contains_photos is None:
            yield{ 
                "subtopic": "Moda",
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": title,
                "date": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get()),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-author"]/text()').get()),
                "text": re.sub( r'\n|\t',"",finaltext),
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
        flag = re.search(r"@",clearcharacters)
        url = response.url
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(clearcharacters)>10 and flag is None:
            yield {
                "subtopic": "Style",
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": title,
                "date": " ".join(re.findall(r"[0-9]+.[α-ωΑ-Ω]+\..[0-9]+",response.xpath('//span[@class="article-date"]/text()').get())),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="author-social"]//h5/a/span[2]/text()').get()),
                "text": re.sub( r'\n|\t',"",clearcharacters),
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
        if title is not None and len(clearcharacters)>10 and flag is None:
            yield {
                "subtopic": "Health & Life",
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": title,
                "date": response.xpath('//time/text()').get(), 
                "author": response.xpath('//span[@class="vcard author"]//a/text()').get(),
                "text": re.sub( r'\s\s\s',"",clearcharacters),
                "url": url,                
            }
    def parseNewpost(self,response):
        title = response.xpath('//h1[@class="article-title"]/text()').get() 
        text = response.xpath('//div[@class="article-main clearfix"]//p/text()|//div[@class="article-main clearfix"]//strong/text()|//div[@class="article-main clearfix"]//p/*/text()').getall()
        listtostring = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",listtostring)
        uneededspaces = re.sub( " ", "",markspaces)
        finaltext = re.sub( "space", " ",uneededspaces)
        clearcharacters = re.sub( "\xa0","",finaltext)
        #flag to see later on if we have tweets ect
        flag = re.search(r"@",clearcharacters)
        url = response.url
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(clearcharacters)>10 and flag is None:
            yield {
                "subtopic": "Lifestyle",
                "website": "newpost.gr",
                "title": title,
                "date": (response.xpath('//small[@class="article-created-time"]/text()').get()).split('/')[0], 
                "author": "Newpost.gr",
                "text": re.sub( r'\s\s\s',"",clearcharacters),
                "url": url,                
        }

    def parse_iefimerida(self,response):
        title = response.xpath('//h1/span/text()').get() 
        text = response.xpath('//div[@class="field--name-body on-container"]//p/text()|//div[@class="field--name-body on-container"]/strong/text()|//div[@class="field--name-body on-container"]//p/*/text()|//div[@class="field--name-body on-container"]//p//li/text()').getall()
        list_to_string = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        final_text = re.sub( "space", " ",uneeded_spaces)
        clear_characters = re.sub("\xa0","",final_text)

        #flag to see later on if we have tweets ect
        flag = re.search(r"@",clear_characters)
        url = response.url
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(final_text)>10 and flag is None:
            yield {
                "subtopic": url.split('/')[3],
                "website": IEFIMERIDA_VARS['AUTHOR'],
                "title": title,
                "date": re.sub(r"\|"," ",re.search(r"(\d+)\|(\d+)\|(\d+)",response.xpath('//span[@class="created"]/text()').get()).group(0)), 
                "author": IEFIMERIDA_VARS['AUTHOR'],
                "text": re.sub( r'\s\s\s|\n',"",final_text),
                "url": url,                
            }