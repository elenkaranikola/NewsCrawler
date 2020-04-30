# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item
from news2.settings import IEFIMERIDA_VARS,TANEA_VARS
from news2.settings import TOVIMA_VARS

class DogSpider(CrawlSpider):
    name = 'food'
    allowed_domains = [
        'tanea.gr',
        'newpost.gr',
        'iefimerida.gr',
        'tovima.gr',
        ]
    url = [
    'http://newpost.gr/gefsi',
    'https://www.iefimerida.gr',
    'https://www.tanea.gr/category/recipes/',
    ]
    tovima_urls = ['https://www.tovima.gr/category/gefsignostis/page/{}'.format(x) for x in range(1,TOVIMA_VARS['FOOD_PAGES'])]
    urls = ['http://newpost.gr/gefsi?page={}'.format(x) for x in range(1,1227)]+['https://www.tanea.gr/category/recipes/page/{}'.format(x) for x in range(1,TANEA_VARS['FOOD_PAGES'])]+tovima_urls
    start_urls = urls[:]  

    rules = ( 
        Rule(LinkExtractor(allow=(r"\.tovima\.gr.+gefsignostis"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tovima', follow=True), 
        Rule(LinkExtractor(allow=(r"\.tanea\.gr.+recipes"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tanea', follow=True), 
        Rule(LinkExtractor(allow=('https://www.iefimerida.gr/gastronomie'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_iefimerida', follow=True), 
        Rule(LinkExtractor(allow=('newpost.gr/gefsi'), deny=()), callback='parseNewpost', follow=True),   
    )
    
    def parseNewpost(self,response):
        title = response.xpath('//h1[@class="article-title"]/text()').get() 
        #text = response.xpath('//div[@class="article-main clearfix"]//strong/text()').getall()
        text = response.xpath('//div[@class="article-main clearfix"]//p/text()|//div[@class="article-main clearfix"]//li/text()|//div[@class="article-main clearfix"]//p/a/strong/text()|//div[@class="article-main clearfix"]//p/*/text()').getall()
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
                "subtopic": "Food",
                "website": "newpost.gr",
                "title": title,
                "date": (response.xpath('//small[@class="article-created-time"]/text()').get()).split('/')[0], 
                "author": "newpost.gr",
                "text": re.sub( r'\s\s\s',"",clearcharacters),
                "url": url,                
        }

    def parse_iefimerida(self,response):
        title = response.xpath('//h1/span/text()').get() 
        text = response.xpath('//div[@class="field--name-body on-container"]//p/text()|//div[@class="field--name-body on-container"]/strong/text()|//div[@class="field--name-body on-container"]//p/*/text()|//div[@class="field--name-body on-container"]//li/text()|//div[@class="field--name-body on-container"]//h2/text()').getall()
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
                "subtopic": "Food",
                "website": IEFIMERIDA_VARS['AUTHOR'],
                "title": title,
                "date": re.sub(r"\|"," ",re.search(r"(\d+)\|(\d+)\|(\d+)",response.xpath('//span[@class="created"]/text()').get()).group(0)), 
                "author": IEFIMERIDA_VARS['AUTHOR'],
                "text": re.sub( r'\s\s\s|\n',"",final_text),
                "url": url,                
            }

    def parse_tanea(self,response):

        title = response.xpath('//h1[@class="entry-title black-c"]/text()').get() 
        #title = " ".join(" ".join(title))
        list_to_string = " ".join(" ".join(title))
        markspaces = re.sub( "       ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        put_spaces_back = re.sub( "space", " ",uneeded_spaces)
        final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)
        #final_title = re.sub(r'/s/s/s',)

        text = response.xpath('//div[@class="main-content pos-rel article-wrapper"]//p/text()|//div[@class="main-content pos-rel article-wrapper"]//strong/text()|//div[@class="main-content pos-rel article-wrapper"]//h3/text()|//div[@class="main-content pos-rel article-wrapper"]//p/*/text()').getall()
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
                "subtopic": 'Recipes',
                "website": TANEA_VARS['AUTHOR'],
                "title": final_title,
                "date": response.xpath('//span[@class="firamedium postdate updated"]/text()').get(), 
                "author": TANEA_VARS['AUTHOR'],
                "text": re.sub( r'\s\s\s|\n',"",final_text),
                "url": url,                
            }

    def parse_tovima(self,response):
        title = response.xpath('//h1[@class="entry-title thirty black-c zonabold"]/text()').get() 
        list_to_string = " ".join(" ".join(title))
        markspaces = re.sub( "       ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        put_spaces_back = re.sub( "space", " ",uneeded_spaces)
        final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

        text = response.xpath('//div[@class="main-content pos-rel article-wrapper"]//p/text()|//div[@class="main-content pos-rel article-wrapper"]//strong/text()|//div[@class="main-content pos-rel article-wrapper"]//h3/text()|//div[@class="main-content pos-rel article-wrapper"]//p/*/text()').getall()
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
                "subtopic": 'Food',
                "website": TOVIMA_VARS['AUTHOR'],
                "title": final_title,
                "date": response.xpath('//time/span/text()').get(), 
                "author": TOVIMA_VARS['AUTHOR'],
                "text": re.sub( r'\s\s\s|\n',"",final_text),
                "url": url,                
            }
