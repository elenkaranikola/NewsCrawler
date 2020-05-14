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
from NewsCrawler.settings import TOPONTIKI_VARS,GENERAL_CATEGORIES
import mysql.connector

class DogSpider(CrawlSpider):
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
        'https://www.protagon.gr/epikairotita/',
        'https://www.iefimerida.gr',
        ]
    topontiki_urls = ['http://www.topontiki.gr/category/perivallon?page={}'.format(x) for x in range(0,TOPONTIKI_VARS['ENVIRONMENT_PAGES'])]
    lifo_urls = ['https://www.lifo.gr/now/perivallon/page:{}'.format(x) for x in range(1,LIFO_VARS['ENVIRONMENT_PAGES'])]
    kathimerini_urls = ['https://www.kathimerini.gr/box-ajax?id=b1_1885015423_1194114316&page={}'.format(x) for x in range(0,KATHIMERINI_VARS['ENVIRONMENT_PAGES'])]
    urls = url + kathimerini_urls + lifo_urls + topontiki_urls
    start_urls = urls[:]

    rules = (
        Rule(LinkExtractor(allow=('topontiki.gr/article/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_topontiki', follow=True), 
        Rule(LinkExtractor(allow=(r'popaganda\.gr.+newstrack/'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_popaganda', follow=True), 
        Rule(LinkExtractor(allow=(r'www\.lifo\.gr.+perivallon'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_lifo', follow=True), 
        Rule(LinkExtractor(allow=(r'www\.lifo\.gr.+environment_articles'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_lifo', follow=True), 
        Rule(LinkExtractor(allow=(r'\.naftemporiki\.gr/story|\.naftemporiki\.gr/storypn'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_naftemporiki', follow=True), 
        Rule(LinkExtractor(allow=(r"\.kathimerini\.gr.+epikairothta/perivallon/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_kathimerini', follow=True), 
        Rule(LinkExtractor(allow=('https://www.iefimerida.gr/green'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_iefimerida', follow=True), 
        Rule(LinkExtractor(allow=('cnn.gr/news/perivallon')), callback='parse_cnn', follow=True),
        Rule(LinkExtractor(allow=('protagon.gr/epikairotita/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_protagon', follow=True), 
        )

    def parse_cnn(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@class="story-title"]/text()').get() 
        if title is not None:
            #get the article's text
            text = response.xpath('//div[@class="story-content"]//p/text()|//div[@class="story-content"]//strong/text()|//div[@class="story-content"]//a/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneede_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneede_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            date = re.sub(r'\n|\t',"",response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get())
            final_date = formatdate(date)

            url = response.url

            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH']:
                yield {
                    "subtopic": GENERAL_CATEGORIES['ENVIRONMENT'],
                    "website": re.search(r"www.+\.gr",url).group(0),
                    "title": title,
                    "article_date": final_date,
                    "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-author"]/text()').get()),
                    "article_body": re.sub( r'\n|\t',"",clear_characters),
                    "url": url,                
                }

    def parse_protagon(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@class="entry-title"]/text()').get()
        if title is not None :
            #check if we are in the correct category
            sub = response.xpath('//span[@class="s_roumpr"]/a/text()').get()
            if sub == PROTAGON_VARS['ENVIRONMENT']:
                #get the article's text
                text = response.xpath('//div[@class="left-single-column "]//p/text()|//div[@class="left-single-column "]//strong/text()|//div[@class="left-single-column "]//p/*/text()').getall()
                list_to_string = " ".join(" ".join(text))
                markspaces = re.sub( "  ", "space",list_to_string)
                uneede_spaces = re.sub( " ", "",markspaces)
                final_text = re.sub( "space", " ",uneede_spaces)
                clear_characters = re.sub( "\xa0","",final_text)

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
                    yield {
                        "subtopic": GENERAL_CATEGORIES['ENVIRONMENT'],
                        "website": re.search(r"www.+\.gr",url).group(0),
                        "title": title,
                        "article_date": final_date, 
                        "author": author,
                        "article_body": re.sub( r'\s\s\s',"",clear_characters),
                        "url": url,                
                    }


    def parse_iefimerida(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1/span/text()').get() 
        if title is not None:
            #get the article's text
            text = response.xpath('//div[@class="field--name-body on-container"]//p/text()|//div[@class="field--name-body on-container"]/strong/text()|//div[@class="field--name-body on-container"]//p/*/text()|//div[@class="field--name-body on-container"]//p//li/text()').getall()
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

            #check if we are in an article and that it doesn't have images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": GENERAL_CATEGORIES['ENVIRONMENT'],
                    "website": IEFIMERIDA_VARS['AUTHOR'],
                    "title": title,
                    "article_date": final_date, 
                    "author": IEFIMERIDA_VARS['AUTHOR'],
                    "article_body": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                }

    def parse_kathimerini(self,response):
        #check if we are in an articles url
        title = response.xpath('//h2[@class="item-title"]/text()').get() 
        if title is not None:
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

            #check if we are in an article and that it doesn't have images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": GENERAL_CATEGORIES['ENVIRONMENT'],
                    "website": KATHIMERINI_VARS['AUTHOR'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": author,
                    "article_body": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                }

    def parse_naftemporiki(self,response):
        #check if we are in an articles url
        title = response.xpath('//h2[@id="sTitle"]/text()').get()
        if title is not None:
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
                list_to_string = " ".join(" ".join(text))
                markspaces = re.sub( "  ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                final_text = re.sub( "space", " ",uneeded_spaces)
                clear_characters = re.sub("\xa0","",final_text)

                date = response.xpath('//div[@class="Date"]/text()').get()
                final_date = formatdate(date)

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url
                
                #check if we are in an article and that it doesn't have images
                if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    yield {
                        "subtopic": response.xpath('//div[@class="Breadcrumb"]/a[2]/text()').get(),
                        "website": NAFTEMPORIKI_VARS['AUTHOR'],
                        "title": final_title,
                        "article_date": final_date,
                        "author": NAFTEMPORIKI_VARS['AUTHOR'],
                        "article_body": re.sub( r'\s\s\s|\n',"",final_text),
                        "url": url,                
                    }


    def parse_lifo(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@itemprop="headline"]/text()|//meta[@itemprop="headline"]/text()|//h1/*/text()').get() 
        if title is not None:
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
            
            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": GENERAL_CATEGORIES['ENVIRONMENT'],
                    "website": LIFO_VARS['AUTHOR'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": author,
                    "article_body": re.sub( r'\s\s\s|\n',"",clear_characters),
                    "url": url,                
                }

    def parse_popaganda(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1/text()').get()
        if title is not None :
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
                list_to_string = " ".join(" ".join(text))
                markspaces = re.sub( "  ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                final_text = re.sub( "space", " ",uneeded_spaces)
                clear_characters = re.sub("\xa0","",final_text)

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
                    yield {
                        "subtopic": POPAGANDA_VARS['ENVIRONMENT'],
                        "website": POPAGANDA_VARS['WEBSITE'],
                        "title": final_title,
                        "article_date": final_date, 
                        "author": POPAGANDA_VARS['WEBSITE'],
                        "article_body": re.sub( r'\s\s\s|\n',"",clear_characters),
                        "url": url,                
                    }

    def parse_topontiki(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1/text()').get() 
        if title is not None:
            #check if we are in the correct category
            sub = response.xpath('//h2/a/text()').get()
            if sub == TOPONTIKI_VARS['CATEGORY_ENVIRONMENT']:
                #fix the title's format
                list_to_string = " ".join(" ".join(title))
                markspaces = re.sub( "       ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                put_spaces_back = re.sub( "space", " ",uneeded_spaces)
                final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

                #get the article's text
                text = response.xpath('//div[@class="field-item even"]//p/text()|//div[@class="field-item even"]//p/*/text()|//div[@class="field-item even"]//p//span/text()').getall()
                list_to_string = " ".join(" ".join(text))
                markspaces = re.sub( "  ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                final_text = re.sub( "space", " ",uneeded_spaces)
                clear_characters = final_text.replace("\xa0","")

                date = response.xpath('//span[@class="date"]/text()').get()
                final_date = formatdate(date)

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url
                
                #check if we are in an article and that it doesn't have images
                if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    yield {
                        "subtopic": GENERAL_CATEGORIES['ENVIRONMENT'],
                        "website": TOPONTIKI_VARS['WEBSITE'],
                        "title": final_title,
                        "article_date": final_date, 
                        "author": TOPONTIKI_VARS['WEBSITE'],
                        "article_body": re.sub( r'\s\s\s|\n',"",clear_characters),
                        "url": url,                
                    }