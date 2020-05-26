# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from NewsCrawler.utilities import formatdate
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from NewsCrawler.items import NewsCrawlerItem
from NewsCrawler.settings import IEFIMERIDA_VARS,TANEA_VARS,TOVIMA_VARS,NEWPOST_VARS
from NewsCrawler.settings import KATHIMERINI_VARS,NAFTEMPORIKI_VARS,IN_VARS
from NewsCrawler.settings import LIFO_VARS,INSOMNIA_VARS,POPAGANDA_VARS,NEWSIT_VARS
from NewsCrawler.settings import GENERAL_CATEGORIES,CNN_VARS,PROTAGON_VARS
import mysql.connector

newsit_counter = 0
popaganda_counter = 0
insomnia_counter = 0
lifo_counter = 0
naftemporiki_counter = 0
kathimerini_counter = 0
tovima_counter = 0
tanea_counter = 0
cnn_counter = 0
protagon_counter = 0
in_counter = 0
newpost_counter = 0
iefimerida_counter = 0

class TechSpider(CrawlSpider):
    name ='tech'
    handle_httpstatus_list = [301, 302]
    allowed_domains = [
        'newsit.gr',
        'popaganda.gr',
        'insomnia.gr',
        'lifo.gr',
        'naftemporiki.gr',
        'kathimerini.gr',
        'tovima.gr',
        'tanea.gr',
        'cnn.gr',
        'protagon.gr',
        'in.gr',
        'newpost.gr',
        'iefimerida.gr',
        ]
    url = [
        'https://www.newsit.gr/category/texnologia/',
        'https://popaganda.gr/newstrack/technews/',
        'https://www.insomnia.gr/articles/',
        'https://www.naftemporiki.gr/techscience',
        'https://www.cnn.gr/tech',
        'https://www.protagon.gr/themata/',
        'https://www.in.gr/tech/',
        'https://newpost.gr/tech',
        ]
    iefimerida_url = ['https://www.iefimerida.gr/tehnologia?page={}'.format(x) for x in range(0,IEFIMERIDA_VARS['TECH_PAGES'])]
    lifo_urls = ['https://www.lifo.gr/now/tech_science/page:{}'.format(x) for x in range(1,LIFO_VARS['TECH_PAGES'])]
    newpost_urls = ['http://newpost.gr/tech?page={}'.format(x) for x in range(1,NEWPOST_VARS['TECH_PAGES'])]
    tanea_urls = ['https://www.tanea.gr/category/science-technology/page/{}'.format(x) for x in range(1,TANEA_VARS['SCIENCE_PAGES'])]
    tovima_urls = ['https://www.tovima.gr/category/science/page/{}'.format(x) for x in range(1,TOVIMA_VARS['SCIENCE_PAGES'])]
    kathimerini_urls = ['https://www.kathimerini.gr/box-ajax?id=b1_1885015423_1385128351&page={}'.format(x) for x in range(0,KATHIMERINI_VARS['SCIENCE_PAGES'])] + ['https://www.kathimerini.gr/box-ajax?id=b5_1885015423_1149063040&page={}'.format(x) for x in range(0,KATHIMERINI_VARS['TECH_PAGES'])]
    urls = url + newpost_urls + tanea_urls + tovima_urls + kathimerini_urls + lifo_urls + iefimerida_url
    start_urls = urls[:]
    

    rules = (
        Rule(LinkExtractor(allow=(r"\.newsit\.gr.+texnologia/"), deny=()), callback='parse_newsit', follow=True ,process_request='process_newsit'), 
        Rule(LinkExtractor(allow=(r'popaganda\.gr.+newstrack/'), deny=('binteo','videos','gallery','eikones','twit','comment','environment','fagito-poto','sport','culture','psichagogia','klp','san-simera-newstrack','keros','kairos','world','estiasi','health','social-media','greece','cosmote','koronoios')), callback='parse_popaganda', follow=True ,process_request='process_popaganda'), 
        Rule(LinkExtractor(allow=('insomnia.gr/articles/'), deny=('page', )), callback='parse_insomnia', follow=True ,process_request='process_insomnia'),
        Rule(LinkExtractor(allow=(r'www\.lifo\.gr.+tech_science/'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_lifo', follow=True ,process_request='process_lifo'), 
        Rule(LinkExtractor(allow=(r'\.naftemporiki\.gr/story|\.naftemporiki\.gr/storypn'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_naftemporiki', follow=True ,process_request='process_naftemporiki'), 
        Rule(LinkExtractor(allow=(r"\.kathimerini\.gr.+epikairothta/episthmh/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_kathimerini_episthmh', follow=True ,process_request='process_kathimerini_epistimi'), 
        Rule(LinkExtractor(allow=(r"\.kathimerini\.gr.+/texnologia/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_kathimerini_tech', follow=True ,process_request='process_kathimerini_tech'), 
        Rule(LinkExtractor(allow=(r"\.tovima\.gr.+science"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tovima', follow=True ,process_request='process_tovima'), 
        Rule(LinkExtractor(allow=(r"\.tanea\.gr.+science-technology"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tanea', follow=True ,process_request='process_tanea'), 
        Rule(LinkExtractor(allow=('iefimerida.gr/tehnologia'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_iefimerida', follow=True ,process_request='process_iefimerida'), 
        Rule(LinkExtractor(allow=('cnn.gr/tech'), deny=('cnn.gr/tech/gallery/')), callback='parse_cnn', follow=True ,process_request='process_cnn'), 
        Rule(LinkExtractor(allow=('protagon.gr/themata/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_protagon', follow=True ,process_request='process_protagon'),
        Rule(LinkExtractor(allow=(r"\.in\.gr.+/tech/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_in', follow=True ,process_request='process_in'), 
        Rule(LinkExtractor(allow=(r"newpost.gr/tech/(\w+).+"), deny=('page')), callback='parse_newpost', follow=True ,process_request='process_newpost'), 
        )

    def parse_newsit(self,response):
        global newsit_counter
        title = response.xpath('//h1/text()').get() 
        if title is not None and newsit_counter < 300:
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            text = response.xpath('//div[@class="entry-content post-with-no-excerpt"]//p/text()|//div[@class="entry-content post-with-no-excerpt"]//strong/text()|//div[@class="entry-content post-with-no-excerpt"]//h3/text()|//div[@class="entry-content post-with-no-excerpt"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub("\xa0","",final_text)

            if len(final_text)<10:
                text = response.xpath('//div[@class="entry-content"]//p/text()|//div[@class="entry-content"]//strong/text()|//div[@class="entry-content"]//h3/text()|//div[@class="entry-content"]//p/*/text()').getall()
                list_to_string = " ".join(" ".join(text))
                markspaces = re.sub( "  ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                final_text = re.sub( "space", " ",uneeded_spaces)
                clear_characters = re.sub("\xa0","",final_text)


            date = response.xpath('//time[@class="entry-date published"]/text()').get()
            final_date = formatdate(date)

            #check if we are in an article, and if it doesn't have images
            if len(final_text)>10 :
                newsit_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['TECH'],
                    "subtopic": GENERAL_CATEGORIES['TECH'],
                    "website": NEWSIT_VARS['WEBSITE'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": NEWSIT_VARS['WEBSITE'],
                    "article_body": re.sub( r'\s\s\s|\n',"",clear_characters),
                    "url": response.url,                
                }

    def process_newsit(self, request):
        global newsit_counter
        if newsit_counter < 300:
            return request

    def parse_cnn(self,response):
        global cnn_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@class="story-title"]/text()').get() 
        if title is not None and cnn_counter < 300:
            #get article's text
            text = response.xpath('//div[@class="story-content"]//p/text()|//div[@class="story-content"]//strong/text()|//div[@class="story-content"]//a/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            date = re.sub(r'\n|\t',"",response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get())
            final_date = formatdate(date)

            #check if we are in an article
            url = response.url
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH']:
                cnn_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['TECH'],
                    "subtopic": GENERAL_CATEGORIES['TECH'],
                    "website": CNN_VARS['WEBSITE'],
                    "title": title,
                    "article_date": final_date,
                    "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-author"]/text()').get()),
                    "article_body": re.sub( r'\n|\t',"",clear_characters),
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
        if title is not None and protagon_counter < 300:
            #check if we are in the correct category
            sub = response.xpath('//span[@class="s_roumpr"]/a/text()').get()
            if sub == PROTAGON_VARS['CATEGORY_TECH']:
                #get article's text 
                text = response.xpath('//div[@class="left-single-column "]//p/text()|//div[@class="left-single-column "]//strong/text()|//div[@class="left-single-column "]//p/*/text()').getall()
                list_to_string = " ".join(" ".join(text))
                markspaces = re.sub( "  ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                final_text = re.sub( "space", " ",uneeded_spaces)
                clear_characters = re.sub( "\xa0","",final_text)

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url

                #get author
                author = re.findall(r"(\w+).(\w+)",response.xpath('//strong[@class="generalbold uppercase"]/a/text()').get())
                list_to_tuple = author[0]
                author = ' '.join(list_to_tuple)

                #get the date the article was published
                date = response.xpath('//span[@class="generalight uppercase"]/text()').get()
                final_date = formatdate(date)

                #check if we are in an article and that it doesn't have images
                if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    protagon_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['TECH'],
                        "subtopic": GENERAL_CATEGORIES['TECH'],
                        "website": PROTAGON_VARS['WEBSITE'],
                        "title": title,
                        "article_date": final_date, 
                        "author": author,
                        "article_body": re.sub( r'\s\s\s',"",clear_characters),
                        "url": url,                
                    }

    def process_protagon(self, request):
        global protagon_counter
        if protagon_counter < 300:
            return request

    def parse_in(self,response):
        global in_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@class="entry-title black-c"]/text()').get() 
        if title is not None and in_counter < 300:
            #get article's text
            text = response.xpath('//div[@class="main-content pos-rel article-wrapper"]//p/text()|//div[@class="main-content pos-rel article-wrapper"]//strong/text()|//div[@class="main-content pos-rel article-wrapper"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            date = response.xpath('//time/text()').get()
            final_date = formatdate(date)

            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                in_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['TECH'],
                    "subtopic": GENERAL_CATEGORIES['TECH'],
                    "website": IN_VARS['WEBSITE'],
                    "title": title,
                    "article_date": final_date, 
                    "author": response.xpath('//span[@class="vcard author"]//a/text()').get(),
                    "article_body": re.sub( r'\s\s\s',"",clear_characters),
                    "url": url,                
                }

    def process_in(self, request):
        global in_counter
        if in_counter < 300:
            return request

    def parse_newpost(self,response):
        global newpost_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@class="article-title"]/text()').get() 
        if title is not None and newpost_counter < 300:
            #get article's text
            text = response.xpath('//div[@class="article-main clearfix"]//p/text()|//div[@class="article-main clearfix"]//strong/text()|//div[@class="article-main clearfix"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            date = (response.xpath('//small[@class="article-created-time"]/text()').get()).split('/')[0]
            date_for_sql_format = formatdate(date)

            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                newpost_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['TECH'],
                    "subtopic": GENERAL_CATEGORIES['TECH'],
                    "website": NEWPOST_VARS['WEBSITE'],
                    "title": title,
                    "article_date": date_for_sql_format, 
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
        if title is not None and iefimerida_counter < 300:
            #get article's text
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
                iefimerida_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['TECH'],
                    "subtopic": GENERAL_CATEGORIES['TECH'],
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

            #get article's text
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
            
            #check if we are in an article and that it doesn't have images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                tanea_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['TECH'],
                    "subtopic":GENERAL_CATEGORIES['TECH'],
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

            #get article's text
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
            
            #check if we are in an article and that it doesn't have images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                tovima_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['TECH'],
                    "subtopic": TOVIMA_VARS['CATEGORY_TECH'],
                    "website": TOVIMA_VARS['AUTHOR'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": TOVIMA_VARS['AUTHOR'],
                    "article_body": re.sub( r'\s\s\s|\n',"",clear_characters),
                    "url": url,                
                }

    def process_tovima(self, request):
        global tovima_counter
        if tovima_counter < 300:
            return request

    def parse_kathimerini_tech(self,response):
        global kathimerini_counter
        #check if we are in an articles url
        title = response.xpath('//h2[@class="item-title"]/text()').get() 
        if title is not None and kathimerini_counter < 300:
            #fix title's format
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            #get article's text
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
            
            #check if we are in an article and that it doesn't have images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                kathimerini_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['TECH'],
                    "subtopic":GENERAL_CATEGORIES['TECH'],
                    "website": KATHIMERINI_VARS['AUTHOR'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": KATHIMERINI_VARS['AUTHOR'],
                    "article_body": re.sub( r'\s\s\s|\n',"",clear_characters),
                    "url": url,                
                }

    def process_kathimerini_tech(self, request):
        global kathimerini_counter
        if kathimerini_counter < 300:
            return request

    def parse_kathimerini_episthmh(self,response):
        #check if we are in an articles url
        global kathimerini_counter
        title = response.xpath('//h2[@class="item-title"]/text()').get() 
        if title is not None and kathimerini_counter < 300:
            #fix title's format
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            #get article's text
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
            
            #get author
            author = response.xpath('//span[@class="item-author"]/a/text()').get()
            if author == KATHIMERINI_VARS['CATEGORY_AUTHOR'] :
                author = KATHIMERINI_VARS['AUTHOR']

            #check if we are in an article and that it doesn't have images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                kathimerini_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['TECH'],
                    "subtopic": KATHIMERINI_VARS['CATEGORY_TECH'],
                    "website": KATHIMERINI_VARS['AUTHOR'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": author,
                    "article_body": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                }

    def process_kathimerini_epistimi(self, request):
        global kathimerini_counter
        if kathimerini_counter < 300:
            return request

    def parse_naftemporiki(self,response):
        global naftemporiki_counter
        #check if we are in an articles url
        title = response.xpath('//h2[@id="sTitle"]/text()').get() 
        if title is not None and naftemporiki_counter < 300:
            #check if we are in the correct category
            subtopic = response.xpath('//span[@itemprop="articleSection"]/text()').get()
            if subtopic == "ΤΕΧΝΟΛΟΓΙΑ-ΕΠΙΣΤΗΜΗ" :
                #fix title's format
                list_to_string = " ".join(" ".join(title))
                markspaces = re.sub( "       ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                put_spaces_back = re.sub( "space", " ",uneeded_spaces)
                final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

                #get article's text
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
                    naftemporiki_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['TECH'],
                        "subtopic": response.xpath('//div[@class="Breadcrumb"]/a[2]/text()').get(),
                        "website": NAFTEMPORIKI_VARS['AUTHOR'],
                        "title": final_title,
                        "article_date": final_date,
                        "author": NAFTEMPORIKI_VARS['AUTHOR'],
                        "article_body": re.sub( r'\s\s\s|\n',"",final_text),
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
        if title is not None and lifo_counter < 300:
            #fix title's format
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            date = response.xpath('//time/text()').get()
            final_date = formatdate(date)

            #get article's text
            text = response.xpath('//div[@class="clearfix wide bodycontent"]//p/text()|//div[@class="clearfix wide bodycontent"]/p/strong/text()|//div[@class="clearfix wide bodycontent"]//h3/text()|//div[@class="clearfix wide bodycontent"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub("\xa0","",final_text)

            #get author
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
                    "topic": GENERAL_CATEGORIES['TECH'],
                    "subtopic": LIFO_VARS['CATEGORY_TECH'],
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

    def parse_insomnia(self,response):
        global insomnia_counter
        #check if we are in an articles url
        title = response.xpath('//div[@class="container"]//h1/text()').get() 
        if title is not None and insomnia_counter < 300:
            #get article's text
            text = response.xpath('//div[@class="the-content"]//p/text()|//div[@class="the-content"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub("\xa0","",final_text)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)

            #find subtopic through url
            url = response.url
            subtopic = url.split('/')[4]

            date = response.xpath('//span[@class="timestamp"]/text()').get()
            final_date = formatdate(date)

            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                insomnia_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['TECH'],
                    "subtopic": subtopic,
                    "website": INSOMNIA_VARS['WEBSITE'],
                    "title": title,
                    "article_date": final_date,
                    "author": response.xpath('//span[@class="author"]/a/text()').get(),
                    "article_body": re.sub( r'\s\s\s|\n|\t',"",clear_characters),
                    "url": response.url,                
                }

    def process_insomnia(self, request):
        global insomnia_counter
        if insomnia_counter < 300:
            return request

    def parse_popaganda(self,response):
        global popaganda_counter
        #check if we are in an articles url
        title = response.xpath('//h1/text()').get()
        if title is not None and popaganda_counter < 300:
            #check if we are in the correct category
            category = response.xpath('//div[@class="category"]/a/text()').get()
            if category == POPAGANDA_VARS['CATEGORY_TECH']:
                #fix title's format
                list_to_string = " ".join(" ".join(title))
                markspaces = re.sub( "       ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                put_spaces_back = re.sub( "space", " ",uneeded_spaces)
                final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

                #get article's text
                text = response.xpath('//div[@class="post-content newstrack-post-content"]//p/text()|//div[@class="post-content newstrack-post-content"]/p/strong/text()|//div[@class="post-content newstrack-post-content"]//h3/text()|//div[@class="post-content newstrack-post-content"]//p/*/text()').getall()
                list_to_string = " ".join(" ".join(text))
                markspaces = re.sub( "  ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                final_text = re.sub( "space", " ",uneeded_spaces)
                clear_characters = re.sub("\xa0","",final_text)

                #get author
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
                        "topic": GENERAL_CATEGORIES['TECH'],
                        "subtopic": POPAGANDA_VARS['TECH'],
                        "website": POPAGANDA_VARS['WEBSITE'],
                        "title": final_title,
                        "article_date": final_date, 
                        "author": POPAGANDA_VARS['WEBSITE'],
                        "article_body": re.sub( r'\s\s\s|\n',"",clear_characters),
                        "url": url,                
                    }

    def process_popaganda(self, request):
        global popaganda_counter
        if popaganda_counter < 300:
            return request 