# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item
from news2.settings import INSOMNIA_VARS

class DogSpider(CrawlSpider):
    name = 'insomnia'
    allowed_domains = ['insomnia.gr']
    start_urls = ['https://www.insomnia.gr/articles/']

    rules = (
        Rule(LinkExtractor(allow=('insomnia.gr/articles/'), deny=('page', )), callback='parse_insomnia', follow=True), 
        )

    def parse_insomnia(self,response):
        text = response.xpath('//div[@class="the-content"]//p/text()|//div[@class="the-content"]//p/*/text()').getall()
        list_to_string = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        final_text = re.sub( "space", " ",uneeded_spaces)
        clear_characters = re.sub("\xa0","",final_text)

        #flag to see later on if we have tweets ect
        flag = re.search(r"@",clear_characters)
        url = response.url
        title = response.xpath('//div[@class="container"]//h1/text()').get() 
        subtopic = url.split('/')[4]
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(clear_characters)>10 and flag is None:
            yield {
                "subtopic": subtopic,
                "website": INSOMNIA_VARS['WEBSITE'],
                "title": title,
                "date": re.search(r'\d+.\d+.\d+',response.xpath('//span[@class="timestamp"]/text()').get()).group(0),
                "author": response.xpath('//span[@class="author"]/a/text()').get(),
                "text": re.sub( r'\s\s\s|\n|\t',"",clear_characters),
                "url": response.url,                
            }
