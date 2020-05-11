# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item
from news2.settings import LIFO_VARS

class DogSpider(CrawlSpider):
    name = 'lifo'
    allowed_domains = ['lifo.gr']
    start_urls = ['https://www.lifo.gr/articles/taste_articles']+['https://www.lifo.gr/syntages']

    rules = (
        Rule(LinkExtractor(allow=(r'www\.lifo\.gr.+syntages/'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_lifo', follow=True), 
        Rule(LinkExtractor(allow=(r'www\.lifo\.gr.+taste_articles/'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_lifo', follow=True), 
        )

    def parse_lifo(self,response):
        title = response.xpath('//h1[@itemprop="headline"]/text()|//meta[@itemprop="headline"]/text()|//h1/*/text()').get() 
        list_to_string = " ".join(" ".join(title))
        markspaces = re.sub( "       ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        put_spaces_back = re.sub( "space", " ",uneeded_spaces)
        final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

        text = response.xpath('//div[@class="clearfix wide bodycontent"]//p/text()|//div[@class="clearfix wide bodycontent"]/p/strong/text()|//div[@class="clearfix wide bodycontent"]//h3/text()|//div[@class="clearfix wide bodycontent"]//p/*/text()').getall()
        list_to_string = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        final_text = re.sub( "space", " ",uneeded_spaces)
        clear_characters = re.sub("\xa0","",final_text)

        author = response.xpath('//div[@class="author"]/a/text()|//div[@itemprop="author"]/*/text()').get()
        if author == None:
            author = LIFO_VARS['AUTHOR']

        #flag to see later on if we have tweets ect
        flag = re.search(r"@",clear_characters)
        url = response.url
        
        subtopic  = response.xpath('//ol/li[3]//span[@itemprop="name"]/text()').get()
        if subtopic == None:
            subtopic = url.split('/')[4]
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(clear_characters)>10 and flag is None:
            yield {
                "subtopic": 'Food',
                "website": LIFO_VARS['AUTHOR'],
                "title": final_title,
                "date": response.xpath('//time/text()').get(), 
                "author": author,
                "text": re.sub( r'\s\s\s|\n',"",clear_characters),
                "url": url,                
            }
