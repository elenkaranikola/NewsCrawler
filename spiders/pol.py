# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item
from news2.settings import PERIODISTA_VARS, PRESSPROJECT_VARS, IEFIMERIDA_VARS,TANEA_VARS,TOVIMA_VARS

class DogSpider(CrawlSpider):
    name = 'pol'
    allowed_domains = [
        'cnn.gr',
        'tovima.gr',
        'reader.gr',
        'thetoc.gr',
        'protagon.gr',
        'periodista.gr',
        'in.gr',
        'newpost.gr',
        'thepressproject.gr',
        'iefimerida.gr',
        'tanea.gr',
        ]

    start_urls = ['https://www.tovima.gr/category/politics/page/{}'.format(x) for x in range(1,TOVIMA_VARS['POLITICS_PAGES'])]

    rules = (
        Rule(LinkExtractor(allow=(r"\.tovima\.gr.+politics"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tovima', follow=True), 
        #Rule(LinkExtractor(allow=(r"\.tanea\.gr.+politics"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tanea', follow=True), 
    )

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
                "subtopic": 'Politics',
                "website": TOVIMA_VARS['AUTHOR'],
                "title": final_title,
                "date": response.xpath('//time/span/text()').get(), 
                "author": TOVIMA_VARS['AUTHOR'],
                "text": re.sub( r'\s\s\s|\n',"",final_text),
                "url": url,                
            }




