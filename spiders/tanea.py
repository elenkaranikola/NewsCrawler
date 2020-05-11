# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item
from news2.settings import TANEA_VARS,GENERAL_CATEGORIES

class DogSpider(CrawlSpider):
    name = 'tanea'
    allowed_domains = ['tanea.gr']
    start_urls = ['https://www.tanea.gr',]
    rules = (
        Rule(LinkExtractor(allow=('greece','politics','economy','world','culture','cinema','lifestyle','music','recipes','science-technology','woman'), deny=('english-edition','binteo','videos','gallery','eikones','twit')), callback='parse_tanea', follow=True), 
        )
    def parse_tanea(self,response):
        title = response.xpath('//h1[@class="entry-title black-c"]/text()').get() 
        if title is not None: 
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
            category = url.split('/')[6]
            if re.search('greece',category) is not None:
                subtopic = GENERAL_CATEGORIES['GREECE']
            elif re.search('politics',category) is not None:
                subtopic = GENERAL_CATEGORIES['WORLD'] 
            elif re.search('economy',category) is not None:
                subtopic = GENERAL_CATEGORIES['ECONOMICS']
            elif re.search('recipes',url) is not None:
                subtopic = GENERAL_CATEGORIES['FOOD']
            elif re.search('lifearts',category) is not None:
                subtopic = url.split('/')[7]
            elif re.search('science-technology',category) is not None:
                subtopic = GENERAL_CATEGORIES['TECH']
            elif re.search('woman',category) is not None:
                subtopic = GENERAL_CATEGORIES['STYLE']
            
            #check if we are in an article and that this article doesn't have any images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": subtopic,
                    "website": TANEA_VARS['AUTHOR'],
                    "title": final_title,
                    "date": response.xpath('//span[@class="firamedium postdate updated"]/text()').get(), 
                    "author": TANEA_VARS['AUTHOR'],
                    "text": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                }



    

