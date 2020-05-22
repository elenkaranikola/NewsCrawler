# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from NewsCrawler.utilities import formatdate
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from NewsCrawler.items import NewsCrawlerItem
from NewsCrawler.settings import PERIODISTA_VARS,IEFIMERIDA_VARS,TANEA_VARS
from NewsCrawler.settings import TOVIMA_VARS,KATHIMERINI_VARS,NAFTEMPORIKI_VARS,CNN_VARS
from NewsCrawler.settings import LIFO_VARS,EFSYN_VARS,POPAGANDA_VARS,PROTAGON_VARS
from NewsCrawler.settings import TOPONTIKI_VARS,GENERAL_CATEGORIES,READER_VARS
from NewsCrawler.settings import PERIODISTA_VARS,NEWPOST_VARS,THETOC_VARS,IN_VARS,NEWSIT_VARS
import mysql.connector

newsit_counter = 0
topontiki_counter = 0
popaganda_counter = 0
efsyn_counter = 0
lifo_counter = 0
cnn_counter = 0
reader_counter = 0
tovima_counter = 0
thetoc_counter = 0
protagon_counter = 0
periodista_counter = 0
in_counter = 0
newpost_counter = 0
iefimerida_counter = 0
tanea_counter = 0
kathimerini_counter = 0
naftemporiki_counter = 0

class GreeceSpider(CrawlSpider):
    name = 'greece'
    allowed_domains = [
        'newsit.gr',
        'topontiki.gr',
        'popaganda.gr',
        'efsyn.gr',
        'lifo.gr',
        'cnn.gr',
        'reader.gr',
        'tovima.gr',
        'thetoc.gr',
        'protagon.gr',
        'periodista.gr',
        'in.gr',
        'newpost.gr',
        'iefimerida.gr',
        'tanea.gr',
        'kathimerini.gr',
        'naftemporiki.gr',
        ]
    url = [
        'https://www.newsit.gr/ellada/',
        'http://www.topontiki.gr/category/ellada',
        'https://popaganda.gr/newstrack/greece-newstrack/',
        'https://www.lifo.gr/now/greece',
        'https://www.naftemporiki.gr/society',
        'https://www.iefimerida.gr',
        'http://www.periodista.gr/',
        'https://www.cnn.gr/',
        'https://www.reader.gr/news/koinonia',
        'https://www.thetoc.gr/',
        'https://www.protagon.gr/epikairotita/ellada',
        'https://www.in.gr/greece/',
        'https://newpost.gr/ellada/',
        'https://www.tanea.gr',
        ]
    efsyn_urls = ['https://www.efsyn.gr/ellada/koinonia?page={}'.format(x) for x in range(1,EFSYN_VARS['GREECE_PAGES'])]
    kathimerini_urls = ['https://www.kathimerini.gr/box-ajax?id=b1_1885015423_50337253&page={}'.format(x) for x in range(0,KATHIMERINI_VARS['GREECE_PAGES'])]
    tovima_urls = ['https://www.tovima.gr/category/society/page/{}'.format(x) for x in range(1,TOVIMA_VARS['GREECE_PAGES'])]
    newpost_urls = ['http://newpost.gr/ellada?page={}'.format(x) for x in range(1,NEWPOST_VARS['GREECE_PAGES'])]
    periodista_urls = ['http://www.periodista.gr/koinwnia?start={}'.format(x) for x in range(1,PERIODISTA_VARS['GREECE_PAGES'],30)]
    urls = url + periodista_urls + newpost_urls + tovima_urls + kathimerini_urls + efsyn_urls
    start_urls = urls[:]

    rules = (
        Rule(LinkExtractor(allow=(r"\.newsit\.gr.+ellada/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_newsit', follow=True ,process_request='process_newsit'), 
        Rule(LinkExtractor(allow=('topontiki.gr/article/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_topontiki', follow=True ,process_request='process_topontiki'), 
        Rule(LinkExtractor(allow=(r'popaganda\.gr.+newstrack/'), deny=('binteo','videos','gallery','eikones','twit','comment','page=','i-omada-tis-efsyn','contact')), callback='parse_popaganda', follow=True ,process_request='process_popaganda'), 
        Rule(LinkExtractor(allow=(r'www\.efsyn\.gr'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_efsyn', follow=True ,process_request='process_efsyn'), 
        Rule(LinkExtractor(allow=(r'\.lifo\.gr.+/greece'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_lifo', follow=True ,process_request='process_lifo'), 
        Rule(LinkExtractor(allow=(r'\.naftemporiki\.gr/story|\.naftemporiki\.gr/storypn'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_naftemporiki', follow=True ,process_request='process_naftemporiki'), 
        Rule(LinkExtractor(allow=(r"\.kathimerini\.gr.+epikairothta/ellada"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_kathimerini', follow=True ,process_request='process_kathimerini'), 
        Rule(LinkExtractor(allow=(r"\.tovima\.gr.+society"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tovima', follow=True ,process_request='process_tovima'), 
        Rule(LinkExtractor(allow=(r"\.tanea\.gr.+greece"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tanea', follow=True ,process_request='process_tanea'), 
        Rule(LinkExtractor(allow=('iefimerida.gr/ellada'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_iefimerida', follow=True ,process_request='process_iefimerida'), 
        Rule(LinkExtractor(allow=('periodista.gr/koinwnia'), deny=('start=')), callback='parse_periodista', follow=True ,process_request='process_periodista'),  
        Rule(LinkExtractor(allow=('thetoc.gr/koinwnia')), callback='parse_thetoc', follow=True ,process_request='process_thetoc'),
        Rule(LinkExtractor(allow=('cnn.gr/news/ellada'), deny=('cnn.gr/news/ellada/gallery/','protoselida')), callback='parse_cnn', follow=True ,process_request='process_cnn'),
        Rule(LinkExtractor(allow=('reader.gr/news/koinonia'), deny=('vid')), callback='parse_reader', follow=True ,process_request='process_reader'), 
        Rule(LinkExtractor(allow=('protagon.gr/epikairotita/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_protagon', follow=True ,process_request='process_protagon'),
        Rule(LinkExtractor(allow=(r".in\.gr.+greece"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_in', follow=True ,process_request='process_in'),
        Rule(LinkExtractor(allow=(r"newpost.gr/ellada/(\w+).+"), deny=()), callback='parse_newpost', follow=True ,process_request='process_newpost'), 
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

            date = response.xpath('//time[@class="entry-date published"]/text()').get()
            final_date = formatdate(date)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            #check if we are in an article, and if it doesn't have images
            if len(final_text)>10 and flag is None:
                newsit_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['GREECE'],
                    "subtopic": GENERAL_CATEGORIES['GREECE'],
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

    def parse_cnn(self,response):
        global cnn_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@class="story-title"]/text()').get() 
        if title is not None and cnn_counter < 300:
            cnn_counter += 1
            text = response.xpath('//div[@class="story-content"]//p/*/text()|//div[@class="story-content"]//p/text()|//div[@class="story-content"]//p/a/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)
            url = response.url

            date = re.sub(r'\n|\t',"",response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get())
            final_date = formatdate(date)
            
            yield {
                "topic": GENERAL_CATEGORIES['GREECE'],
                "subtopic": GENERAL_CATEGORIES['GREECE'],
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
        if title is not None and reader_counter < 300 :
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
                author = READER_VARS["AUTHOR"]

            url = response.url
            yield {
                "topic": GENERAL_CATEGORIES['GREECE'],
                "subtopic": GENERAL_CATEGORIES['GREECE'],
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
        if title is not None and thetoc_counter < 300 :
            thetoc_counter += 1
            text = response.xpath('//div[@class="article-content articleText"]//p/text()|//div[@class="article-content articleText"]//strong/text()|//div[@class="article-content articleText"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            date = response.xpath('//span[@class="article-date"]/text()').get()
            final_date = THETOC_VARS['full_date'] +formatdate(date)
            
            url = response.url
            if len(clear_characters)> GENERAL_CATEGORIES['ALLOWED_LENGTH']:
                yield {
                    "topic": GENERAL_CATEGORIES['GREECE'],
                    "subtopic": GENERAL_CATEGORIES['GREECE'],
                    "website": THETOC_VARS['WEBSITE'],
                    "title": title,
                    "article_date": final_date,
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
        if title is not None and protagon_counter < 300 :
            #check if we are in the correct category
            sub = response.xpath('//span[@class="s_roumpr"]/a/text()').get()
            if sub == PROTAGON_VARS['CATEGORY_GREECE']:            
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

                #check if we are in an article and that this article doesn't have any images
                if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    protagon_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['GREECE'],
                        "subtopic": GENERAL_CATEGORIES['GREECE'],
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
            url = response.url

            date = response.xpath('//div[@class="col-md-4 per-color-grey per-font-size-md per-padding-top-20"]/text()').get()
            final_date = formatdate(date)

            #flag to see later on if we have videos
            flag = re.search(r"binteo|foto",url)

            #check if we are in an article and that this article doesn't have any images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                periodista_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['GREECE'],
                    "subtopic": GENERAL_CATEGORIES['GREECE'],
                    "website": PERIODISTA_VARS['WEBSITE'],
                    "title": re.sub( r'\t|\n|\r',"",title),
                    "article_date": final_date,  
                    "author": PERIODISTA_VARS['WEBSITE'],
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
        if title is not None and in_counter < 300 :
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

            #check if we are in an article and that this article doesn't have any images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                in_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['GREECE'],
                    "subtopic": GENERAL_CATEGORIES['GREECE'],
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
        if title is not None and newpost_counter < 300 :
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

            #check if we are in an article and that this article doesn't have any images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                newpost_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['GREECE'],
                    "subtopic": GENERAL_CATEGORIES['GREECE'],
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

            #check if we are in an article and that this article doesn't have any images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                iefimerida_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['GREECE'],
                    "subtopic": GENERAL_CATEGORIES['GREECE'],
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
        title = response.xpath('//h1[@class="entry-title black-c"]/text()').get() 
        #check if we are in an articles url
        if title is not None and tanea_counter < 300 :
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
            #check if we are in an article and that this article doesn't have any images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                tanea_counter +=1
                yield {
                    "topic": GENERAL_CATEGORIES['GREECE'],
                    "subtopic": GENERAL_CATEGORIES['GREECE'],
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
        #check if we are in an articles urls
        title = response.xpath('//h1[@class="entry-title thirty black-c zonabold"]/text()').get() 
        if title is not None and tovima_counter < 300 :
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
            
            #check if we are in an article and that this article doesn't have any images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                tovima_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['GREECE'],
                    "subtopic": GENERAL_CATEGORIES['GREECE'],
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
        #check if we are in an articles urls
        title = response.xpath('//h2[@class="item-title"]/text()').get() 
        if title is not None and kathimerini_counter < 300 :
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

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
            if author == "Κύριο Αρθρο" :
                author = KATHIMERINI_VARS['AUTHOR']

            #check if we are in an article and that this article doesn't have any images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                kathimerini_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['GREECE'],
                    "subtopic": GENERAL_CATEGORIES['GREECE'],
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

    def parse_naftemporiki(self,response):
        global naftemporiki_counter
        #check if we are in an articles urls
        title = response.xpath('//h2[@id="sTitle"]/text()').get()
        if title is not None and naftemporiki_counter < 300 :
            #check if we are in the correct category
            subtopic = response.xpath('//span[@itemprop="articleSection"]/text()').get()
            if subtopic == NAFTEMPORIKI_VARS['CATEGORY_GREECE'] :
                
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
                
                #check if we are in an article and that this article doesn't have any images
                if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    naftemporiki_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['GREECE'],
                        "subtopic": GENERAL_CATEGORIES['GREECE'],
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
        #check if we are in an articles urls
        title = response.xpath('//h1[@itemprop="headline"]/text()|//meta[@itemprop="headline"]/text()|//h1/*/text()').get() 
        if title is not None and lifo_counter < 300 :
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            date = response.xpath('//time/text()').get()
            final_date = formatdate(date)

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
            
            #check if we are in an article and that this article doesn't have any images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                lifo_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['GREECE'],
                    "subtopic": GENERAL_CATEGORIES['GREECE'],
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

    def parse_efsyn(self,response):
        global efsyn_counter
        #check if we are in an articles urls
        title = response.xpath('//h1[1]/text()').get() 
        if title is not None and efsyn_counter < 300:
            #check if we are in the correct category
            subtopic = response.xpath('//article/a/@href').get()
            category = subtopic.split('/')[1]
            if category == EFSYN_VARS['CATEGORY_GREECE']:
                
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
                
                #check if we are in an article and that this article doesn't have any images
                if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    efsyn_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['GREECE'],
                        "subtopic": GENERAL_CATEGORIES['GREECE'],
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

    def parse_popaganda(self,response):
        global popaganda_counter
        #check if we are in an articles urls
        title = response.xpath('//h1/text()').get()
        if title is not None and popaganda_counter < 300:
            #check if we are in the correct category
            category = response.xpath('//div[@class="category"]/a/text()').get()
            if category == POPAGANDA_VARS['CATEGORY_GREECE'] :

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

                date = response.xpath('//div[@class="date"]/text()|//div[@class="fullscreen-date"]/text()').get()
                final_date = formatdate(date)

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url

                #check if we are in an article and that this article doesn't have any images
                if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    popaganda_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['GREECE'],
                        "subtopic": GENERAL_CATEGORIES['GREECE'],
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

    def parse_topontiki(self,response):
        global topontiki_counter
        #check if we are in an articles urls
        title = response.xpath('//h1/text()').get() 
        if title is not None and topontiki_counter < 300 : 
            #check if we are in the correct category
            sub = response.xpath('//h2/a/text()').get()
            if sub == TOPONTIKI_VARS['CATEGORY_GREECE']:
                
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
                
                #check if we are in an article and that this article doesn't have any images
                if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    topontiki_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['GREECE'],
                        "subtopic": GENERAL_CATEGORIES['GREECE'],
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