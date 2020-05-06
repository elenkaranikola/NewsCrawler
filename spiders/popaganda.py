# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item
from news2.settings import POPAGANDA_VARS

class DogSpider(CrawlSpider):
    name = 'popaganda'
    allowed_domains = ['popaganda.gr']
    start_urls = ['https://popaganda.gr/table/']

    rules = (
        Rule(LinkExtractor(allow=(r'popaganda\.gr.+table.+'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_popaganda', follow=True), 
    )

    def parse_popaganda(self,response):
        title = response.xpath('//h1/text()').get() 
        list_to_string = " ".join(" ".join(title))
        markspaces = re.sub( "       ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        put_spaces_back = re.sub( "space", " ",uneeded_spaces)
        final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

        text = response.xpath('//div[@class="post-content newstrack-post-content"]//p/text()|//div[@class="post-content newstrack-post-content"]/p/strong/text()|//div[@class="post-content newstrack-post-content"]//h3/text()|//div[@class="post-content newstrack-post-content"]//p/*/text()').getall()
        list_to_string = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        final_text = re.sub( "space", " ",uneeded_spaces)
        clear_characters = re.sub("\xa0","",final_text)

        author = response.xpath('//div[@class="author"]/a/text()|//div[@itemprop="author"]/*/text()').get()
        if author == None:
            author = POPAGANDA_VARS['WEBSITE']

        #flag to see later on if we have tweets ect
        flag = re.search(r"@",clear_characters)
        url = response.url

        #check if we are in an article, and if it doesn't have images
        if title is not None and len(clear_characters)>10 and flag is None:
            yield {
                "subtopic": POPAGANDA_VARS['FOOD'],
                "website": POPAGANDA_VARS['WEBSITE'],
                "title": final_title,
                "date": re.search(r'\d+\.\d+\.\d+',response.xpath('//div[@class="date"]/text()').get()).group(0), 
                "author": POPAGANDA_VARS['WEBSITE'],
                "text": re.sub( r'\s\s\s|\n',"",clear_characters),
                "url": url,                
            }
