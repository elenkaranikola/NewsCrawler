# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from NewsCrawler.utilities import formatdate
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from NewsCrawler.items import NewsCrawlerItem
from NewsCrawler.settings import PERIODISTA_VARS,NEWSIT_VARS,IEFIMERIDA_VARS,TANEA_VARS
from NewsCrawler.settings import TOVIMA_VARS,NAFTEMPORIKI_VARS,EFSYN_VARS,READER_VARS
from NewsCrawler.settings import TOPONTIKI_VARS,GENERAL_CATEGORIES, NEWPOST_VARS
from NewsCrawler.settings import PROTAGON_VARS,THETOC_VARS,IN_VARS,CNN_VARS
import mysql.connector

#global counters
naftemporiki_counter = 0
tanea_counter = 0
cnn_counter = 0
reader_counter = 0
thetoc_counter = 0
protagon_counter = 0
in_counter = 0
newsit_counter = 0
iefimerida_counter = 0
topontiki_counter = 0
efsyn_counter = 0
tovima_counter = 0
periodista_counter = 0
newpost_counter = 0

class EconomicSpider(CrawlSpider):
    name = 'economics'
    allowed_domains = [
        'topontiki.gr',
        'efsyn.gr',
        'naftemporiki.gr',
        'tovima.gr',
        'tanea.gr',
        'cnn.gr',
        'reader.gr',
        'thetoc.gr',
        'protagon.gr',
        'periodista.gr',
        'in.gr',
        'newpost.gr',
        'newsit.gr',
        'iefimerida.gr',
        ]
    url = [
        'https://www.naftemporiki.gr/finance/economy',
        'https://www.tanea.gr',
        'https://www.cnn.gr/',
        'https://www.reader.gr/news/oikonomia',
        'https://www.thetoc.gr/',
        'https://www.protagon.gr/epikairotita/',
        'http://www.periodista.gr/oikonomia',
        'https://www.in.gr/economy/',
        'http://newpost.gr/',
        'https://www.newsit.gr/category/oikonomia/',
        'https://www.iefimerida.gr',
        ]
    topontiki_urls = ['http://www.topontiki.gr/category/oikonomia?page={}'.format(x) for x in range(0,TOPONTIKI_VARS['ECONOMICS_PAGES'])]
    efsyn_urls = ['https://www.efsyn.gr/oikonomia?page={}'.format(x) for x in range(1,EFSYN_VARS['ECONOMICS_PAGES'])]
    to_vima_urls = ['https://www.tovima.gr/category/finance/page/{}'.format(x) for x in range(1,TOVIMA_VARS['ECONOMICS_PAGES'])]
    newpost_urls = ['http://newpost.gr/oikonomia?page={}'.format(x) for x in range(1,NEWPOST_VARS['ECONOMICS_PAGES'])]
    periodista_urls = ['http://www.periodista.gr/oikonomia?start={}'.format(x) for x in range(1,PERIODISTA_VARS['ECONOMY_PAGES'],30)]
    urls = url + to_vima_urls + newpost_urls + periodista_urls + efsyn_urls + topontiki_urls
    start_urls = urls[:]

    rules = (
        Rule(LinkExtractor(allow=('topontiki.gr/article/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_topontiki', follow=True ,process_request='process_topontiki'), 
        Rule(LinkExtractor(allow=(r'www\.efsyn\.gr.+node/'), deny=('binteo','videos','gallery','eikones','twit','comment','page=','i-omada-tis-efsyn','contact')), callback='parse_efsyn', follow=True ,process_request='process_efsyn'), 
        Rule(LinkExtractor(allow=(r"\.naftemporiki\.gr.+finance/story"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_naftemporiki', follow=True,process_request='process_naftemporiki'), 
        Rule(LinkExtractor(allow=(r"\.tovima\.gr.+finance"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tovima', follow=True ,process_request='process_tovima'), 
        Rule(LinkExtractor(allow=(r"\.tanea\.gr.+economy"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tanea', follow=True ,process_request='process_tanea'),
        Rule(LinkExtractor(allow=('iefimerida.gr/oikonomia'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_iefimerida', follow=True ,process_request='process_iefimerida'), 
        Rule(LinkExtractor(allow=(r"\.newsit\.gr.+oikonomia/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_newsit', follow=True ,process_request='process_newsit'), 
        Rule(LinkExtractor(allow=('periodista.gr/oikonomia'), deny=('start=')), callback='parse_periodista', follow=True, process_request='process_periodista'),
        Rule(LinkExtractor(allow=('cnn.gr/oikonomia'), deny=('cnn.gr/oikonomia/gallery/')), callback='parse_cnn', follow=True ,process_request='process_cnn'), 
        Rule(LinkExtractor(allow=('reader.gr/news/oikonomia'), deny=('vid')), callback='parse_reader', follow=True ,process_request='process_reader'),
        Rule(LinkExtractor(allow=('thetoc.gr/oikonomia'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_thetoc', follow=True ,process_request='process_thetoc'),
        Rule(LinkExtractor(allow=('protagon.gr/epikairotita/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_protagon', follow=True ,process_request='process_protagon'),
        Rule(LinkExtractor(allow=(r"\.in\.gr.+/economy/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_in', follow=True ,process_request='process_in'), 
        Rule(LinkExtractor(allow=(r"newpost.gr/oikonomia/(\w+).+"), deny=()), callback='parse_newpost', follow=True ,process_request='process_newpost'), 
        )

    def parse_cnn(self,response):
        global cnn_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@class="story-title"]/text()').get() 
        if title is not None and cnn_counter <300:

            text = response.xpath('//div[@class="story-content"]//p/text()|//div[@class="story-content"]//strong/text()|//div[@class="story-content"]//a/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            date = re.sub(r'\n|\t',"",response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get())
            final_date = formatdate(date)

            url = response.url
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH']:
                cnn_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['ECONOMICS'],
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
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

    def parse_reader(self,response):
        global reader_counter
        #check if we are in an articles url
        title = response.xpath('//h1/text()').get() 
        if title is not None and reader_counter<300:
            reader_counter += 1

            text = response.xpath('//div[@class="article-summary"]//p/text()|//div[@class="article-body"]//p/text()|//div[@class="article-body"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            date = response.xpath('//time/text()').get()
            final_date = formatdate(date)

            author = response.xpath('//p[@class="article-author"]/a/text()').get()
            if author is not None:
                author = re.sub("\xa0","",author)
            else:
                author = READER_VARS['AUTHOR']

            url = response.url
            yield {
                "topic": GENERAL_CATEGORIES['ECONOMICS'],
                "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
                "website": READER_VARS['WEBSITE'],
                "title": re.sub( r'\n|\t',"",title),
                "article_date": final_date,
                "author": author,
                "article_body": re.sub( r'\n|\t',"",clear_characters),
                "url": url,              
            }
    def process_reader(self, request):
        global reader_counter
        if reader_counter < 300:
            return request

    def parse_thetoc(self,response):
        global thetoc_counter
        #check if we are in an articles url
        title = response.xpath('//div[@class="article-title"]//h1/text()').get() 
        if title is not None and thetoc_counter < 300:
            text = response.xpath('//div[@class="article-content articleText"]//p/text()|//div[@class="article-content articleText"]//strong/text()|//div[@class="article-content articleText"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            date = response.xpath('//span[@class="article-date"]/text()').get()
            final_date = THETOC_VARS['full_date'] +formatdate(date)

            url = response.url
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH']:
                thetoc_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['ECONOMICS'],
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
                    "website": re.search(r"www.+\.gr",url).group(0),
                    "title": title,
                    "article_date":final_date,
                    "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="author-social"]//h5/a/span[2]/text()').get()),
                    "article_body": re.sub( r'\n|\t',"",clear_characters),
                    "url": url,                
                }
    def process_thetoc(self, request):
        global thetoc_counter
        if thetoc_counter < 300:
            return request

    def parse_protagon(self,response):
        global protagon_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@class="entry-title"]/text()').get()
        if title is not None and protagon_counter <300 :
            #check if we are in the correct category
            sub = response.xpath('//span[@class="s_roumpr"]/a/text()').get()
            if sub == PROTAGON_VARS['CATEGORY_ECONOMICS']:
 
                text = response.xpath('//div[@class="left-single-column "]//p/text()|//div[@class="left-single-column "]//strong/text()|//div[@class="left-single-column "]//p/*/text()').getall()
                list_to_string = " ".join(" ".join(text))
                markspaces = re.sub( "  ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                final_text = re.sub( "space", " ",uneeded_spaces)
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
                    protagon_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['ECONOMICS'],
                        "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
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

    def parse_periodista(self,response):
        global periodista_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@itemprop="headline"]/text()').get() 
        if title is not None and periodista_counter < 300 :
            text = response.xpath('//div[@class="per-item-page-part per-article-body"]//p/text()|//div[@class="per-item-page-part per-article-body"]//strong/text()|//div[@class="per-item-page-part per-article-body"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            date = response.xpath('//div[@class="col-md-4 per-color-grey per-font-size-md per-padding-top-20"]/text()').get()
            final_date = formatdate(date)

            #flag to see later on if we have videos
            url = response.url
            flag = re.search(r"binteo|foto",url)

            #check if we are in an article and that it doesn't have videos
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                periodista_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['ECONOMICS'],
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
                    "website": PERIODISTA_VARS['WEBSITE'],
                    "title": re.sub( r'\t|\n|\r',"",title),
                    "article_date": final_date, 
                    "author": "periodista.gr",
                    "article_body": re.sub( r'\s\s\s',"",clear_characters),
                    "url": url,                
                }  
    def process_periodista(self, request):
        global periodista_counter
        if periodista_counter < 300:
            return request
            

    def parse_in(self,response):
        global in_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@class="entry-title black-c"]/text()').get() 
        if title is not None and in_counter < 300:

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

            #check if we are in an article and that it doesn't have any images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                in_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['ECONOMICS'],
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
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
            final_date = formatdate(date)

            #check if we are in an article and that it doesn't have any images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                newpost_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['ECONOMICS'],
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
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

            date = response.xpath('//time[@class="entry-date published"]/text()').get()
            final_date = formatdate(date)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            #check if we are in an article, and if it doesn't have images
            if len(final_text)>10 and flag is None:
                newsit_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['ECONOMICS'],
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
                    "website": NEWSIT_VARS['WEBSITE'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": NEWSIT_VARS['WEBSITE'],
                    "article_body": re.sub( r'\s\s\s|\n',"",clear_characters),
                    "url": url,                
                }

    def process_newsit(self, request):
        global newsit_counter
        if newsit_counter < 300:
            return request                

    def parse_iefimerida(self,response):
        global iefimerida_counter
        #check if we are in an articles url
        title = response.xpath('//h1/span/text()').get() 
        if title is not None and iefimerida_counter < 300:

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

            #check if we are in an article and that it doesn't have any images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                iefimerida_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['ECONOMICS'],
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
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

            date = response.xpath('//span[@class="firamedium postdate updated"]/text()').get()
            final_date = formatdate(date)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            #check if we are in an article and that it doesn't have any images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                tanea_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['ECONOMICS'],
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
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

            date = response.xpath('//time/span/text()').get()
            final_date = formatdate(date)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            
            #check if we are in an article and that it doesn't have any images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                tovima_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['ECONOMICS'],
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
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

    def parse_naftemporiki(self,response):
        global naftemporiki_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@id="sTitle"]/text()').get() 
        if title is not None and naftemporiki_counter < 300:
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            date = response.xpath('//div[@class="Date"]/text()').get()
            final_date = formatdate(date)

            text = response.xpath('//div[@class="entityMain article"]//p/text()|//div[@class="entityMain article"]/p/strong/text()|//div[@class="entityMain article"]//h3/text()|//div[@class="entityMain article"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub("\xa0","",final_text)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            
            #check if we are in an article and that it doesn't have any images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                naftemporiki_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['ECONOMICS'],
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
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

    def parse_efsyn(self,response):
        global efsyn_counter 
        #check if we are in an articles url
        title = response.xpath('//h1[1]/text()').get() 
        if title is not None and efsyn_counter < 300 :
            #check if we are in the correct category
            subtopic = response.xpath('//article/a/@href').get()
            category = subtopic.split('/')[1]
            if category == EFSYN_VARS['CATEGORY_ECONOMICS']:
                list_to_string = " ".join(" ".join(title))
                markspaces = re.sub( "       ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                put_spaces_back = re.sub( "space", " ",uneeded_spaces)
                final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

                text = response.xpath('//div[@class="article__body js-resizable"]//p/text()|//div[@class="article__body js-resizable"]/p/strong/text()|//div[@class="article__body js-resizable"]//h3/text()|//div[@class="article__body js-resizable"]//p/*/text()').getall()
                list_to_string = " ".join(" ".join(text))
                markspaces = re.sub( "  ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                final_text = re.sub( "space", " ",uneeded_spaces)
                clear_characters = re.sub("\xa0","",final_text)

                author = response.xpath('//div[@class="article__author"]//a/text()').get()
                if author == None:
                    author = response.xpath('//div[@class="article__author"]/span/text()').get()

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url

                date = response.xpath('//time/text()').get()
                final_date = formatdate(date)
                
                #check if we are in an article and that it doesn't have any images
                if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    efsyn_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['ECONOMICS'],
                        "subtopic": EFSYN_VARS['ECONOMICS'],
                        "website": EFSYN_VARS['WEBSITE'],
                        "title": final_title,
                        "article_date": final_date, 
                        "author": author,
                        "article_body": re.sub( r'\s\s\s|\n',"",clear_characters),
                        "url": url,                
                    }

    def process_efsyn(self, request):
        global efsyn_counter
        if efsyn_counter < 300:
            return request 

    def parse_topontiki(self,response):
        global topontiki_counter
        #check if we are in an articles url
        title = response.xpath('//h1/text()').get()
        if title is not None and topontiki_counter < 300:
            #check if we are in the correct category
            sub = response.xpath('//h2/a/text()').get()
            if sub == TOPONTIKI_VARS['CATEGORY_ECONOMICS']:
                 
                list_to_string = " ".join(" ".join(title))
                markspaces = re.sub( "       ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                put_spaces_back = re.sub( "space", " ",uneeded_spaces)
                final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

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
                
                #check if we are in an article and that it doesn't have any images
                if title is not None and len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    topontiki_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['ECONOMICS'],
                        "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
                        "website": TOPONTIKI_VARS['WEBSITE'],
                        "title": final_title,
                        "article_date": final_date, 
                        "author": TOPONTIKI_VARS['WEBSITE'],
                        "article_body": re.sub( r'\s\s\s|\n',"",clear_characters),
                        "url": url,                
                    }
    def process_topontiki(self, request):
        global topontiki_counter
        if topontiki_counter < 300:
            return request 