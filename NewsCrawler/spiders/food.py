# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from NewsCrawler.utilities import formatdate
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from NewsCrawler.items import NewsCrawlerItem
from NewsCrawler.settings import IEFIMERIDA_VARS,TANEA_VARS,POPAGANDA_VARS,NEWPOST_VARS
from NewsCrawler.settings import TOVIMA_VARS,KATHIMERINI_VARS,LIFO_VARS,GENERAL_CATEGORIES
import mysql.connector

popaganda_counter = 0
lifo_counter = 0
kathimerini_counter = 0
tanea_counter = 0
newpost_counter = 0
iefimerida_counter = 0
tovima_counter = 0

class FoodSpider(CrawlSpider):
    name = 'food'
    allowed_domains = [
        'popaganda.gr',
        'lifo.gr',
        'kathimerini.gr',
        'tanea.gr',
        'newpost.gr',
        'iefimerida.gr',
        'tovima.gr',
        ]
    url = [
        'https://popaganda.gr/table/pou-trone-i-sef-table/',
        'https://popaganda.gr/table/spirits/',
        'https://popaganda.gr/table/street-food/',
        'https://popaganda.gr/table/estiatoria-details/',
        'https://popaganda.gr/table/spirits/',
        'https://popaganda.gr/table/greek-producers/',
        'https://www.lifo.gr/articles/taste_articles',
        'https://www.lifo.gr/syntages',
        'http://newpost.gr/gefsi',
        'https://www.iefimerida.gr',
        'https://www.tanea.gr/category/recipes/',
    ]
    kathimerini_urls = ['https://www.kathimerini.gr/box-ajax?id=b17_2041842937_413381051&page={}'.format(x) for x in range(0,KATHIMERINI_VARS['FOOD_PAGES'])] + ['https://www.kathimerini.gr/box-ajax?id=b3_2041842937_900635337&page={}'.format(x) for x in range(0,KATHIMERINI_VARS['FOOD_PAGES'])]
    tovima_urls = ['https://www.tovima.gr/category/gefsignostis/page/{}'.format(x) for x in range(1,TOVIMA_VARS['FOOD_PAGES'])]
    newpost_urls = ['http://newpost.gr/gefsi?page={}'.format(x) for x in range(1,NEWPOST_VARS['FOOD_PAGES'])]
    tanea_urls = ['https://www.tanea.gr/category/recipes/page/{}'.format(x) for x in range(1,TANEA_VARS['FOOD_PAGES'])]
    urls = kathimerini_urls + newpost_urls + tovima_urls + tanea_urls
    start_urls = urls[:]  

    rules = ( 
        Rule(LinkExtractor(allow=('popaganda.gr/table'), deny=('binteo','videos','gallery','eikones','twit','comment','environment','sport','technews','psichagogia','klp','culture','san-simera-newstrack','keros','kairos','world','estiasi','health','social-media','greece','cosmote','koronoios')), callback='parse_popaganda', follow=True ,process_request='process_popaganda'), 
        Rule(LinkExtractor(allow=(r'www\.lifo\.gr.+syntages/'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_lifo', follow=True ,process_request='process_lifo'), 
        Rule(LinkExtractor(allow=(r'www\.lifo\.gr.+taste_articles/'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_lifo', follow=True ,process_request='process_lifo'), 
        Rule(LinkExtractor(allow=(r"\.kathimerini\.gr.+gastronomos/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_kathimerini', follow=True ,process_request='process_kathimerini'), 
        Rule(LinkExtractor(allow=(r"\.tovima\.gr.+gefsignostis"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tovima', follow=True ,process_request='process_tovima'), 
        Rule(LinkExtractor(allow=(r"\.tanea\.gr.+recipes"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tanea', follow=True ,process_request='process_tanea'), 
        Rule(LinkExtractor(allow=('https://www.iefimerida.gr/gastronomie'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_iefimerida', follow=True ,process_request='process_iefimerida'), 
        Rule(LinkExtractor(allow=(r"newpost.gr/gefsi/(\w+).+"), deny=()), callback='parse_newpost', follow=True ,process_request='process_newpost'),   
    )
    
    def parse_newpost(self,response):
        global newpost_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@class="article-title"]/text()').get() 
        if title is not None and newpost_counter < 300:
            #get the article's text
            text = response.xpath('//div[@class="article-main clearfix"]//p/text()|//div[@class="article-main clearfix"]//li/text()|//div[@class="article-main clearfix"]//p/a/strong/text()|//div[@class="article-main clearfix"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            date = (response.xpath('//small[@class="article-created-time"]/text()').get()).split('/')[0]
            final_date = formatdate(date)

            #check if we are in an article and that it doesn't have any images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                newpost_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['FOOD'],
                    "subtopic": GENERAL_CATEGORIES['FOOD'],
                    "website": NEWPOST_VARS['WEBSITE'],
                    "title": title,
                    "article_date": final_date, 
                    "author": NEWPOST_VARS['WEBSITE'],
                    "article_body": re.sub( r'\s\s\s',"",clear_characters),
                    "url": url,                
            }
    def process_newpost(self, request):
        global newpost_counter
        if newpost_counter < 300:
            return request

    def parse_iefimerida(self,response):
        global iefimerida_counter
        #check if we are in an articles url
        title = response.xpath('//h1/span/text()').get() 
        if title is not None and iefimerida_counter < 300 :
            #get the article's text
            text = response.xpath('//div[@class="field--name-body on-container"]//p/text()|//div[@class="field--name-body on-container"]/strong/text()|//div[@class="field--name-body on-container"]//p/*/text()|//div[@class="field--name-body on-container"]//li/text()|//div[@class="field--name-body on-container"]//h2/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub("\xa0","",final_text)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            date = response.xpath('//span[@class="created"]/text()').get()
            final_date = formatdate(date)

            #check if we are in an article and that it doesn't have any images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None:
                iefimerida_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['FOOD'],
                    "subtopic": GENERAL_CATEGORIES['FOOD'],
                    "website": IEFIMERIDA_VARS['AUTHOR'],
                    "title": title,
                    "article_date": final_date, 
                    "author": IEFIMERIDA_VARS['AUTHOR'],
                    "article_body": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                }
    def process_iefimerida(self, request):
        global iefimerida_counter
        if iefimerida_counter < 300:
            return request

    def parse_tanea(self,response):
        global tanea_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@class="entry-title black-c"]/text()').get() 
        if title is not None and tanea_counter < 300:
            #fix title's format
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            #get the article's text
            text = response.xpath('//div[@class="main-content pos-rel article-wrapper"]//p/text()|//div[@class="main-content pos-rel article-wrapper"]//strong/text()|//div[@class="main-content pos-rel article-wrapper"]//h3/text()|//div[@class="main-content pos-rel article-wrapper"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub("\xa0","",final_text)

            date = response.xpath('//span[@class="firamedium postdate updated"]/text()').get()
            final_date = formatdate(date)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            
            #check if we are in an article and that it doesn't have any images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None:
                tanea_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['FOOD'],
                    "subtopic": GENERAL_CATEGORIES['FOOD'],
                    "website": TANEA_VARS['AUTHOR'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": TANEA_VARS['AUTHOR'],
                    "article_body": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                }

    def process_tanea(self, request):
        global tanea_counter
        if tanea_counter < 300:
            return request

    def parse_tovima(self,response):
        global tovima_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@class="entry-title thirty black-c zonabold"]/text()').get() 
        if title is not None and tovima_counter < 300:
            #fix title's format
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            #get the article's text
            text = response.xpath('//div[@class="main-content pos-rel article-wrapper"]//p/text()|//div[@class="main-content pos-rel article-wrapper"]//strong/text()|//div[@class="main-content pos-rel article-wrapper"]//h3/text()|//div[@class="main-content pos-rel article-wrapper"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub("\xa0","",final_text)

            date = response.xpath('//time/span/text()').get()
            final_date = formatdate(date)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            
            #check if we are in an article and that it doesn't have any images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None:
                tovima_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['FOOD'],
                    "subtopic": GENERAL_CATEGORIES['FOOD'],
                    "website": TOVIMA_VARS['AUTHOR'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": TOVIMA_VARS['AUTHOR'],
                    "article_body": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                }

    def process_tovima(self, request):
        global tovima_counter
        if tovima_counter < 300:
            return request

    def parse_kathimerini(self,response):
        global kathimerini_counter
        #check if we are in an articles url
        title = response.xpath('//h2[@class="item-title"]/text()').get() 
        if title is not None and kathimerini_counter < 300 :
            #fix title's format
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            #get the article's text
            text = response.xpath('//div[@class="freetext"]//p/text()|//div[@class="freetext"]//strong/text()|//div[@class="freetext"]//h3/text()|//div[@class="freetext"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub("\xa0","",final_text)

            date = response.xpath('//time/text()').get()
            final_date = formatdate(date)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            
            author = response.xpath('//span[@class="item-author"]/a/text()').get()
            if author == KATHIMERINI_VARS['CATEGORY_AUTHOR'] :
                author = KATHIMERINI_VARS['AUTHOR']
            #check if we are in an article and that it doesn't have any images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None:
                kathimerini_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['FOOD'],
                    "subtopic": response.xpath('//span[@class="item-category"]/a/text()').get(),
                    "website": KATHIMERINI_VARS['AUTHOR'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": author,
                    "article_body": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                }

    def process_kathimerini(self, request):
        global kathimerini_counter
        if kathimerini_counter < 300:
            return request

    def parse_lifo(self,response):
        global lifo_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@itemprop="headline"]/text()|//meta[@itemprop="headline"]/text()|//h1/*/text()').get() 
        if title is not None and lifo_counter < 300 :
            #fix title's format
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            date = response.xpath('//time/text()').get()
            final_date = formatdate(date)

            #get the article's text
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

            #check if we are in an article and that it doesn't have any images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None:
                lifo_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['FOOD'],
                    "subtopic": GENERAL_CATEGORIES['FOOD'],
                    "website": LIFO_VARS['AUTHOR'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": author,
                    "article_body": re.sub( r'\s\s\s|\n',"",clear_characters),
                    "url": url,                
                }

    def process_lifo(self, request):
        global lifo_counter
        if lifo_counter < 300:
            return request


    def parse_popaganda(self,response):
        global popaganda_counter 
        #check if we are in an articles url
        title = response.xpath('//h1/text()').get() 
        if title != None and popaganda_counter < 30 :
            #fix title's format
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            uneeded_escapes = re.sub(r'\n|\s\s\s',"",put_spaces_back)
            final_title = re.sub("\xa0","",uneeded_escapes)

            #get the article's text
            text = response.xpath('//div[@class="post-content big nxContent"]//p/text()|//div[@class="post-content big nxContent"]//strong/text()|//div[@class="post-content big nxContent"]//span/*/text()|//div[@class="post-content big nxContent"]//em/text()|//div[@class="post-content big nxContent"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub(r'\s\s\s|\n',"",final_text)

            date = response.xpath('//div[@class="article_date"]/text()|//div[@class="fullscreen-date"]/text()').get()
            final_date = formatdate(date)

            author = response.xpath('//div[@class="author-title"]/a/text()|//div[@itemprop="author-title"]/*/text()|//div[@class="fullscreen-author"]/a/text()').get()
            if author == None:
                author = POPAGANDA_VARS['WEBSITE']

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)   
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None:
                popaganda_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['FOOD'],
                    "subtopic": POPAGANDA_VARS['FOOD'],
                    "website": POPAGANDA_VARS['WEBSITE'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": re.sub(r'\n',"",author),
                    "article_body": clear_characters.replace(" ","",1),
                    "url": response.url,
                }

    def process_popaganda(self, request):
        global popaganda_counter
        if popaganda_counter < 300:
            return request