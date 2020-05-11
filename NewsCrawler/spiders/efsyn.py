# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item
from news2.settings import EFSYN_VARS

class DogSpider(CrawlSpider):
    name = 'efsyn'
    allowed_domains = ['efsyn.gr']
    start_urls = ['https://www.efsyn.gr/tehnes?page={}'.format(x) for x in range(1,EFSYN_VARS['ART_PAGES'])]

    rules = (
        Rule(LinkExtractor(allow=(r'www\.efsyn\.gr'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_efsyn', follow=True), 
    )

    def parse_efsyn(self,response):
        subtopic = response.xpath('//article/a/@href').get()
        category = subtopic.split('/')[1]
        if category == "tehnes":
            title = response.xpath('//h1[1]/text()').get() 
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            text = response.xpath('//div[@class="article__body js-resizable"]//p/text()|//div[@class="article__body js-resizable"]/p/strong/text()|//div[@class="article__body js-resizable"]//h3/text()|//div[@class="article__body js-resizable"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub("\xa0","",final_text)

            author = response.xpath('//div[@class="article__author"]//a/text()').get()
            if author == None:
                author = response.xpath('//div[@class="article__author"]/span/text()').get()

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            

            #check if we are in an article, and if it doesn't have images
            if title is not None and len(clear_characters)>10 and flag is None:
                yield {
                    "subtopic": EFSYN_VARS['ART'],
                    "website": EFSYN_VARS['WEBSITE'],
                    "title": final_title,
                    "date": response.xpath('//time/text()').get(), 
                    "author": author,
                    "text": re.sub( r'\s\s\s|\n',"",clear_characters),
                    "url": url,                
                }
