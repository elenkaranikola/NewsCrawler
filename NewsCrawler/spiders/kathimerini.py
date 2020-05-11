# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item
from news2.settings import KATHIMERINI_VARS
#from scrapy.conf import settings

class DogSpider(CrawlSpider):
    name = 'kathimerini'
    allowed_domains = ['kathimerini.gr']
    urls = ['https://www.kathimerini.gr/box-ajax?id=b1_1885015423_50337253&page={}'.format(x) for x in range(1,KATHIMERINI_VARS['GREECE_PAGES'])]
    start_urls = urls[:]



    rules = (
        Rule(LinkExtractor(allow=(r"\.kathimerini\.gr.+ellada/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_kathimerini', follow=True), 
        )

    def parse_kathimerini(self,response):
        title = response.xpath('//h2[@class="item-title"]/text()').get() 
        list_to_string = " ".join(" ".join(title))
        markspaces = re.sub( "       ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        put_spaces_back = re.sub( "space", " ",uneeded_spaces)
        final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

        text = response.xpath('//div[@class="freetext"]//p/text()|//div[@class="freetext"]//strong/text()|//div[@class="freetext"]//h3/text()|//div[@class="freetext"]//p/*/text()').getall()
        list_to_string = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        final_text = re.sub( "space", " ",uneeded_spaces)
        clear_characters = re.sub("\xa0","",final_text)

        #flag to see later on if we have tweets ect
        flag = re.search(r"@",clear_characters)
        url = response.url
        
        author = response.xpath('//span[@class="item-author"]/a/text()').get()
        if author == "Κύριο Αρθρο" :
            author = KATHIMERINI_VARS['AUTHOR']
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(final_text)>10 and flag is None:
            yield {
                "subtopic": response.xpath('//span[@class="item-category"]/a/text()').get(),
                "website": KATHIMERINI_VARS['AUTHOR'],
                "title": final_title,
                "date": re.search(r"(\d+).(\w+).(\d+)",response.xpath('//time/text()').get()).group(0), 
                "author": author,
                "text": re.sub( r'\s\s\s|\n',"",final_text),
                "url": url,                
            }


