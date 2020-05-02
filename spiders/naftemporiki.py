# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item
from news2.settings import NAFTEMPORIKI_VARS

class DogSpider(CrawlSpider):
    name = 'naftemporiki'
    allowed_domains = ['naftemporiki.gr']
    start_urls = ['https://www.naftemporiki.gr/politics']

    rules = (
        Rule(LinkExtractor(allow=(r'\.naftemporiki\.gr/story|\.naftemporiki\.gr/storypn'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_naftemporiki', follow=True), 
        )

    def parse_naftemporiki(self,response):
        subtopic = response.xpath('//span[@itemprop="articleSection"]/text()').get()
        if subtopic == "ΠΟΛΙΤΙΚΗ" :
            title = response.xpath('//h2[@id="sTitle"]/text()').get() 
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            text = response.xpath('//div[@class="entityMain article"]//p/text()|//div[@class="entityMain article"]/p/strong/text()|//div[@class="entityMain article"]//h3/text()|//div[@class="entityMain article"]//p/*/text()').getall()
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
                    "subtopic": 'Politics',
                    "website": NAFTEMPORIKI_VARS['AUTHOR'],
                    "title": final_title,
                    "date": response.xpath('//div[@class="Date"]/text()').get(), 
                    "author": NAFTEMPORIKI_VARS['AUTHOR'],
                    "text": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                }
