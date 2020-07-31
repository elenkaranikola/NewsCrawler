# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from NewsCrawler.utilities import formatdate
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from NewsCrawler.items import NewsCrawlerItem
from NewsCrawler.settings import IEFIMERIDA_VARS,KATHIMERINI_VARS,NAFTEMPORIKI_VARS
from NewsCrawler.settings import LIFO_VARS,POPAGANDA_VARS,PROTAGON_VARS
from NewsCrawler.settings import TOPONTIKI_VARS,GENERAL_CATEGORIES,CNN_VARS
import mysql.connector

topontiki_counter = 0
popaganda_counter = 0
lifo_counter = 0
naftemporiki_counter = 0
kathimerini_counter = 0
cnn_counter = 0
protagon_counter = 0
iefimerida_counter = 0

class EnvironmentSpider(CrawlSpider):
    name = 'environment'
    allowed_domains = [
        'topontiki.gr',
        'popaganda.gr',
        'lifo.gr',
        'naftemporiki.gr',
        'kathimerini.gr',
        'cnn.gr',
        'protagon.gr',
        'iefimerida.gr',
        
    ]
    url = [
        'https://popaganda.gr/newstrack/environment/',
        'https://www.naftemporiki.gr/green',
        'https://www.cnn.gr/',
        'https://www.protagon.gr/epikairotita/perivallon-epikairotita',
        'https://www.iefimerida.gr',
        ]
    iefimerida_url = ['https://www.iefimerida.gr/green?page={}'.format(x) for x in range(0,IEFIMERIDA_VARS['ENVIRONMENT_PAGES'])]
    topontiki_urls = ['http://www.topontiki.gr/category/perivallon?page={}'.format(x) for x in range(0,TOPONTIKI_VARS['ENVIRONMENT_PAGES'])]
    lifo_urls = ['https://www.lifo.gr/now/perivallon/page:{}'.format(x) for x in range(1,LIFO_VARS['ENVIRONMENT_PAGES'])]
    kathimerini_urls = ['https://www.kathimerini.gr/box-ajax?id=b1_1885015423_1194114316&page={}'.format(x) for x in range(0,KATHIMERINI_VARS['ENVIRONMENT_PAGES'])]
    urls = url + kathimerini_urls + lifo_urls + topontiki_urls + iefimerida_url
    start_urls = urls[:]


    rules = (
        Rule(LinkExtractor(allow=('topontiki.gr/article/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_topontiki', follow=True ,process_request='process_topontiki'), 
        Rule(LinkExtractor(allow=(r'popaganda\.gr.+newstrack/'), deny=('binteo','videos','gallery','eikones','twit','comment','culture','fagito-poto','sport','technews','psichagogia','klp','san-simera-newstrack','keros','kairos','world','estiasi','health','social-media','greece','cosmote','koronoios')), callback='parse_popaganda', follow=True ,process_request='process_popaganda'), 
        Rule(LinkExtractor(allow=(r'www\.lifo\.gr.+perivallon'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_lifo', follow=True ,process_request='process_lifo'), 
        Rule(LinkExtractor(allow=(r'www\.lifo\.gr.+environment_articles'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_lifo', follow=True ,process_request='process_lifo'), 
        Rule(LinkExtractor(allow=(r'\.naftemporiki\.gr/story|\.naftemporiki\.gr/storypn'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_naftemporiki', follow=True ,process_request='process_naftemporiki'), 
        Rule(LinkExtractor(allow=(r"\.kathimerini\.gr.+epikairothta/perivallon/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_kathimerini', follow=True ,process_request='process_kathimerini'), 
        Rule(LinkExtractor(allow=('iefimerida.gr/green'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_iefimerida', follow=True ,process_request='process_iefimerida'), 
        Rule(LinkExtractor(allow=('cnn.gr/perivallon')), callback='parse_cnn', follow=True ,process_request='process_cnn'),
        Rule(LinkExtractor(allow=('protagon.gr/epikairotita/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_protagon', follow=True ,process_request='process_protagon'), 
        )

    def parse_cnn(self,response):
        global cnn_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@class="main-title"]/text()').get() 
        if title is not None and cnn_counter <300:

            text = response.xpath('//div[@class="main-content story-content"]//p/text()|//div[@class="main-content story-content"]//strong/text()|//div[@class="main-content story-content"]//a/text()').getall()
            list_to_string = " ".join(text)
            no_spaces_text = re.findall(r'[/<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
            final_text = " ".join(no_spaces_text)
            clear_characters = re.sub( "\xa0"," ",final_text)

            date = re.sub(r'\n|\t',"",response.xpath('//time/text()').get())
            final_date = formatdate(date)

            url = response.url

            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH']:
                cnn_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['ENVIRONMENT'],
                    "subtopic": GENERAL_CATEGORIES['ENVIRONMENT'],
                    "website": CNN_VARS['WEBSITE'],
                    "title": title,
                    "article_date": final_date,
                    "author": re.sub(r'\n|\t',"",response.xpath('//a[@class="author-name"]/text()|//span[@class="author-name"]/text()').get()),
                    "article_body": clear_characters,
                    "url": url,                
                }

    def process_cnn(self, request):
        global cnn_counter
        if cnn_counter < 300:
            return request

    def parse_protagon(self,response):
        global protagon_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@class="entry-title"]/text()').get()
        if title is not None and protagon_counter < 300 :
            #check if we are in the correct category
            sub = response.xpath('//span[@class="s_roumpr"]/a/text()').get()
            if sub == PROTAGON_VARS['CATEGORY_ENVIRONMENT']:
                #get the article's text
                text = response.xpath('//div[@class="left-single-column "]//p/text()|//div[@class="left-single-column "]//strong/text()|//div[@class="left-single-column "]//p/*/text()').getall()
                list_to_string = " ".join(text)
                no_spaces_text = re.findall(r'[/<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
                final_text = " ".join(no_spaces_text)
                clear_characters = re.sub( "\xa0"," ",final_text)

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url

                author = re.findall(r"(\w+).(\w+)",response.xpath('//strong[@class="generalbold uppercase"]/a/text()').get())
                list_to_tuple = author[0]
                author = ' '.join(list_to_tuple)
                
                date = response.xpath('//span[@class="generalight uppercase"]/text()').get()
                final_date = formatdate(date)

                #check if we are in an article and that it doesn't have images
                if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    protagon_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['ENVIRONMENT'],
                        "subtopic": GENERAL_CATEGORIES['ENVIRONMENT'],
                        "website": PROTAGON_VARS['WEBSITE'],
                        "title": title,
                        "article_date": final_date, 
                        "author": author,
                        "article_body": clear_characters,
                        "url": url,                
                    }

    def process_protagon(self, request):
        global protagon_counter
        if protagon_counter < 300:
            return request

    def parse_iefimerida(self,response):
        global iefimerida_counter
        #check if we are in an articles url
        title = response.xpath('//h1/span/text()').get() 
        if title is not None and iefimerida_counter < 300 :
            #get the article's text
            text = response.xpath('//div[@class="field--name-body on-container"]//p/text()|//div[@class="field--name-body on-container"]/strong/text()|//div[@class="field--name-body on-container"]//p/*/text()|//div[@class="field--name-body on-container"]//p//li/text()').getall()
            list_to_string = " ".join(text)
            no_spaces_text = re.findall(r'[/<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
            final_text = " ".join(no_spaces_text)
            clear_characters = re.sub( "\xa0"," ",final_text)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            date = response.xpath('//span[@class="created"]/text()').get()
            final_date = formatdate(date)

            #check if we are in an article and that it doesn't have images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                iefimerida_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['ENVIRONMENT'],
                    "subtopic": GENERAL_CATEGORIES['ENVIRONMENT'],
                    "website": IEFIMERIDA_VARS['AUTHOR'],
                    "title": title,
                    "article_date": final_date, 
                    "author": IEFIMERIDA_VARS['AUTHOR'],
                    "article_body": clear_characters,
                    "url": url,                
                }

    def process_iefimerida(self, request):
        global iefimerida_counter
        if iefimerida_counter < 300:
            return request

    def parse_kathimerini(self,response):
        global kathimerini_counter
        #check if we are in an articles url
        title = response.xpath('//h2[@class="item-title"]/text()').get() 
        if title is not None and kathimerini_counter < 300 :
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            #get the article's text
            text = response.xpath('//div[@class="freetext"]//p/text()|//div[@class="freetext"]//strong/text()|//div[@class="freetext"]//h3/text()|//div[@class="freetext"]//p/*/text()').getall()
            list_to_string = " ".join(text)
            no_spaces_text = re.findall(r'[/<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
            final_text = " ".join(no_spaces_text)
            clear_characters = re.sub( "\xa0"," ",final_text)

            date = response.xpath('//time/text()').get()
            final_date = formatdate(date)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            
            author = response.xpath('//span[@class="item-author"]/a/text()').get()
            if author == KATHIMERINI_VARS['CATEGORY_AUTHOR'] :
                author = KATHIMERINI_VARS['AUTHOR']

            #check if we are in an article and that it doesn't have images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                kathimerini_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['ENVIRONMENT'],
                    "subtopic": GENERAL_CATEGORIES['ENVIRONMENT'],
                    "website": KATHIMERINI_VARS['AUTHOR'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": author,
                    "article_body": clear_characters,
                    "url": url,                
                }

    def process_kathimerini(self, request):
        global kathimerini_counter
        if kathimerini_counter < 300:
            return request

    def parse_naftemporiki(self,response):
        global naftemporiki_counter
        #check if we are in an articles url
        title = response.xpath('//h2[@id="sTitle"]/text()').get()
        if title is not None and naftemporiki_counter < 300 :
            #check if we are in the correct category
            subtopic = response.xpath('//span[@itemprop="articleSection"]/text()').get()
            if subtopic == NAFTEMPORIKI_VARS['CATEGORY_ENVIRONMENT'] :
                #fix the title's format
                list_to_string = " ".join(" ".join(title))
                markspaces = re.sub( "       ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                put_spaces_back = re.sub( "space", " ",uneeded_spaces)
                final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

                #get the article's text
                text = response.xpath('//div[@class="entityMain article"]//p/text()|//div[@class="entityMain article"]/p/strong/text()|//div[@class="entityMain article"]//h3/text()|//div[@class="entityMain article"]//p/*/text()').getall()
                list_to_string = " ".join(text)
                no_spaces_text = re.findall(r'[/<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
                final_text = " ".join(no_spaces_text)
                clear_characters = re.sub( "\xa0"," ",final_text)

                date = response.xpath('//div[@class="Date"]/text()').get()
                final_date = formatdate(date)

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url
                
                #check if we are in an article and that it doesn't have images
                if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    naftemporiki_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['ENVIRONMENT'],
                        "subtopic": response.xpath('//div[@class="Breadcrumb"]/a[2]/text()').get(),
                        "website": NAFTEMPORIKI_VARS['AUTHOR'],
                        "title": final_title,
                        "article_date": final_date,
                        "author": NAFTEMPORIKI_VARS['AUTHOR'],
                        "article_body": clear_characters,
                        "url": url,                
                    }

    def process_naftemporiki(self, request):
        global naftemporiki_counter
        if naftemporiki_counter < 300:
            return request

    def parse_lifo(self,response):
        global lifo_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@itemprop="headline"]/text()|//meta[@itemprop="headline"]/text()|//h1/*/text()').get() 
        if title is not None and lifo_counter < 300 :
            #fix the title's format
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            date = response.xpath('//time/text()').get()
            final_date = formatdate(date)

            #get the article's text
            text = response.xpath('//div[@class="clearfix wide bodycontent"]//p/text()|//div[@class="clearfix wide bodycontent"]/p/strong/text()|//div[@class="clearfix wide bodycontent"]//h3/text()|//div[@class="clearfix wide bodycontent"]//p/*/text()').getall()
            list_to_string = " ".join(text)
            no_spaces_text = re.findall(r'[/<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
            final_text = " ".join(no_spaces_text)
            clear_characters = re.sub( "\xa0"," ",final_text)

            author = response.xpath('//div[@class="author"]/a/text()|//div[@itemprop="author"]/*/text()').get()
            if author == None:
                author = LIFO_VARS['AUTHOR']

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            
            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                lifo_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['ENVIRONMENT'],
                    "subtopic": GENERAL_CATEGORIES['ENVIRONMENT'],
                    "website": LIFO_VARS['AUTHOR'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": author,
                    "article_body": clear_characters,
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
        if title is not None and popaganda_counter < 300 :
            #check if we are in the correct category
            category = response.xpath('//div[@class="category"]/a/text()').get()
            if category == POPAGANDA_VARS['CATEGORY_ENVIRONMENT']:
                #fix the title's format
                list_to_string = " ".join(" ".join(title))
                markspaces = re.sub( "       ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                put_spaces_back = re.sub( "space", " ",uneeded_spaces)
                final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

                #get the article's text
                text = response.xpath('//div[@class="post-content newstrack-post-content"]//p/text()|//div[@class="post-content newstrack-post-content"]/p/strong/text()|//div[@class="post-content newstrack-post-content"]//h3/text()|//div[@class="post-content newstrack-post-content"]//p/*/text()').getall()
                list_to_string = " ".join(text)
                no_spaces_text = re.findall(r'[/<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
                final_text = " ".join(no_spaces_text)
                clear_characters = re.sub( "\xa0"," ",final_text)

                author = response.xpath('//div[@class="author"]/a/text()|//div[@itemprop="author"]/*/text()').get()
                if author == None:
                    author = POPAGANDA_VARS['WEBSITE']

                date = response.xpath('//div[@class="date"]/text()|//div[@class="fullscreen-date"]/text()').get()
                final_date = formatdate(date)

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url

                #check if we are in an article and that it doesn't have images
                if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    popaganda_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['ENVIRONMENT'],
                        "subtopic": POPAGANDA_VARS['ENVIRONMENT'],
                        "website": POPAGANDA_VARS['WEBSITE'],
                        "title": final_title,
                        "article_date": final_date, 
                        "author": POPAGANDA_VARS['WEBSITE'],
                        "article_body": clear_characters,
                        "url": url,                
                    }

    def process_popaganda(self, request):
        global popaganda_counter
        if popaganda_counter < 300:
            return request

    def parse_topontiki(self,response):
        global topontiki_counter
        #check if we are in an articles url
        title = response.xpath('//h1/text()').get() 
        if title is not None and topontiki_counter < 300 :
            #check if we are in the correct category
            sub = response.xpath('//h2/a/text()').get()
            if sub == TOPONTIKI_VARS['CATEGORY_ENVIRONMENT']:
                #fix the title's format
                list_to_string_title = "".join(title)  

                #get the article's text
                text = response.xpath('//div[@class="field-item even"]//p/text()|//div[@class="field-item even"]//p/*/text()|//div[@class="field-item even"]//p//span/text()').getall()
                list_to_string = " ".join(text)
                text = re.findall(r'[<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
                final_text = " ".join(text)
                clear_characters = final_text.replace("\xa0"," ")

                date = response.xpath('//span[@class="date"]/text()').get()
                final_date = formatdate(date)

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url
                
                #check if we are in an article and that it doesn't have images
                if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    topontiki_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['ENVIRONMENT'],
                        "subtopic": GENERAL_CATEGORIES['ENVIRONMENT'],
                        "website": TOPONTIKI_VARS['WEBSITE'],
                        "title": list_to_string_title,
                        "article_date": final_date, 
                        "author": TOPONTIKI_VARS['WEBSITE'],
                        "article_body": re.sub( r'\s\s\s|\n',"",clear_characters),
                        "url": url,                
                    }

    def process_topontiki(self, request):
        global topontiki_counter
        if topontiki_counter < 300:
            return request