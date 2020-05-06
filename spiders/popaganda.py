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
    urls = ['https://popaganda.gr/table/spirits/']+['https://popaganda.gr/table/greek-producers/']
    start_urls = ['https://popaganda.gr/table/estiatoria-details/','https://popaganda.gr/table/street-food/','https://popaganda.gr/table/spirits/','https://popaganda.gr/table/pou-trone-i-sef-table/'] + urls

    rules = (
        Rule(LinkExtractor(allow=('popaganda.gr/table'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_popaganda', follow=True), 
    )

    def parse_popaganda(self,response):

        title = response.xpath('//h1/text()').get() 
        if title != None:
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            uneeded_escapes = re.sub(r'\n|\s\s\s',"",put_spaces_back)
            final_title = re.sub("\xa0","",uneeded_escapes)

            text = response.xpath('//div[@class="post-content big nxContent"]//p/text()|//div[@class="post-content big nxContent"]//strong/text()|//div[@class="post-content big nxContent"]//span/*/text()|//div[@class="post-content big nxContent"]//em/text()|//div[@class="post-content big nxContent"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub(r'\s\s\s|\n',"",final_text)

            author = response.xpath('//div[@class="author-title"]/a/text()|//div[@itemprop="author-title"]/*/text()|//div[@class="fullscreen-author"]/a/text()').get()
            if author == None:
                author = POPAGANDA_VARS['WEBSITE']

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)   
            if len(clear_characters)>10 and flag is None:
                yield {
                    "subtopic": POPAGANDA_VARS['FOOD'],
                    "website": POPAGANDA_VARS['WEBSITE'],
                    "title": final_title,
                    "date": re.search(r'\d+\.\d+\.\d+',response.xpath('//div[@class="date"]/text()|//div[@class="fullscreen-date"]/text()').get()).group(0), 
                    "author": re.sub(r'\n',"",author),
                    "text": clear_characters.replace(" ","",1),
                    "url": response.url,
                }

