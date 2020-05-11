# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item
from news2.settings import TOPONTIKI_VARS,GENERAL_CATEGORIES

class DogSpider(CrawlSpider):
    custom_settings = {
        'DEPTH_LIMIT': '1',
    }
    name = 'topontiki'
    allowed_domains = ['topontiki.gr']
    start_urls = ['http://www.topontiki.gr/category/p-art?page={}'.format(x) for x in range(0,TOPONTIKI_VARS['CULTURE_PAGES'])]

    rules = (
        Rule(LinkExtractor(allow=('topontiki.gr/article/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_topontiki', follow=True), 
        )

    def parse_topontiki(self,response):
        sub = response.xpath('//h2/a[1]/text()').get()
        if sub == TOPONTIKI_VARS['CATEGORY_CULTURE']:
            title = response.xpath('//h1/text()').get() 
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            text = response.xpath('//div[@class="field-item even"]//p/text()|//div[@class="field-item even"]//p/*/text()|//div[@class="field-item even"]//p//span/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = final_text.replace("\xa0","")

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            
            #check if we are in an article, and if it doesn't have images
            if title is not None and len(clear_characters)>10 and flag is None:
                yield {
                    "subtopic": GENERAL_CATEGORIES['CULTURE'],
                    "website": TOPONTIKI_VARS['WEBSITE'],
                    "title": final_title,
                    "date": response.xpath('//span[@class="date"]/text()').get(), 
                    "author": response.xpath('//a[@class="author"]/text()').get(),
                    "text": re.sub( r'\s\s\s|\n',"",clear_characters),
                    "url": url,                
                }

