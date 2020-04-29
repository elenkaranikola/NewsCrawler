# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item
from news2.settings import IEFIMERIDA_VARS

class DogSpider(CrawlSpider):
    name = 'food'
    allowed_domains = [
        'newpost.gr',
        'iefimerida.gr',
        ]
    url = [
    'http://newpost.gr/gefsi',
    'https://www.iefimerida.gr',
    ]
    urls = ['http://newpost.gr/gefsi?page={}'.format(x) for x in range(1,1227)]
    start_urls = urls[:]  
    rules = ( 
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