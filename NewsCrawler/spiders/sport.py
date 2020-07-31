# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from NewsCrawler.utilities import formatdate
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from NewsCrawler.items import NewsCrawlerItem
from NewsCrawler.settings import PERIODISTA_VARS,IEFIMERIDA_VARS,TANEA_VARS,NEWSIT_VARS
from NewsCrawler.settings import TOVIMA_VARS,KATHIMERINI_VARS,NAFTEMPORIKI_VARS
from NewsCrawler.settings import POPAGANDA_VARS,TOPONTIKI_VARS,GENERAL_CATEGORIES
from NewsCrawler.settings import NEWPOST_VARS,SPORT24_VARS,GAZZEETTA_VARS,CNN_VARS
from NewsCrawler.settings import NEWPOST_VARS,READER_VARS,IN_VARS,THETOC_VARS,PROTAGON_VARS
import mysql.connector

newsit_counter = 0
topontiki_counter = 0
popaganda_counter = 0
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
gazzetta_counter = 0
sport24_counter = 0
cnn_counter = 0


class SportSpider(CrawlSpider):
    name = 'sport'
    allowed_domains = [
        'newsit.gr',
        'topontiki.gr',
        'popaganda.gr',
        'naftemporiki.gr',
        'kathimerini.gr',
        'tovima.gr',
        'tanea.gr',
        'gazzetta.gr',
        'sport24.gr',
        'cnn.gr',
        'reader.gr',
        'thetoc.gr',
        'protagon.gr',
        'in.gr',
        'newpost.gr',
        'periodista.gr',
        'iefimerida.gr',
        ]
    url = [
        'https://www.newsit.gr/category/athlitika/',
        'https://popaganda.gr/newstrack/sports/',
        'https://www.naftemporiki.gr/sports',
        'https://www.tanea.gr/category/sports/',
        'https://www.iefimerida.gr/spor',
        'http://www.gazzetta.gr/',
        'https://www.sport24.gr',
        'https://www.cnn.gr/sports',
        'https://www.reader.gr/athlitismos',
        'https://www.thetoc.gr/athlitika',
        'https://www.protagon.gr/epikairotita/',
        'https://www.in.gr/sports/',
        'https://newpost.gr/athlitika',
        ]
    thetoc_urls = ['https://www.thetoc.gr/athlitika/?page={}'.format(x) for x in range(1,THETOC_VARS['SPORT_PAGES'])]
    topontiki_urls = ['http://www.topontiki.gr/category/athlitika?page={}'.format(x) for x in range(0,TOPONTIKI_VARS['SPORT_PAGES'])]
    kathimerini_urls = ['https://www.kathimerini.gr/box-ajax?id=b1_1885015423_371795634&page={}'.format(x) for x in range(0,KATHIMERINI_VARS['SPORT_PAGES'])] 
    newpost_urls = ['http://newpost.gr/athlitika?page={}'.format(x) for x in range(1,NEWPOST_VARS['SPORT_PAGES'])]
    periodista_urls = ['http://www.periodista.gr/athlhtika-paraskhnia?start={}'.format(x) for x in range(0,PERIODISTA_VARS['SPORT_PAGES'],30)]
    tovima_urls = ['https://www.tovima.gr/category/sports/page/{}'.format(x) for x in range(1,TOVIMA_VARS['SPORT_PAGES'])]
    urls = url + kathimerini_urls + newpost_urls + periodista_urls + tovima_urls + topontiki_urls
    start_urls = urls[:]

    rules = (
        Rule(LinkExtractor(allow=(r"\.newsit\.gr.+athlitika/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_newsit', follow=True ,process_request='process_newsit'),        
        Rule(LinkExtractor(allow=('topontiki.gr/article/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_topontiki', follow=True ,process_request='process_topontiki'), 
        Rule(LinkExtractor(allow=(r'popaganda\.gr.+newstrack/'), deny=('binteo','videos','gallery','eikones','twit','comment','environment','fagito-poto','culture','technews','psichagogia','klp','san-simera-newstrack','keros','kairos','world','estiasi','health','social-media','greece','cosmote','koronoios')), callback='parse_popaganda', follow=True ,process_request='process_popaganda'), 
        Rule(LinkExtractor(allow=(r'\.naftemporiki\.gr/story|\.naftemporiki\.gr/storypn'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_naftemporiki', follow=True ,process_request='process_naftemporiki'), 
        Rule(LinkExtractor(allow=(r"\.kathimerini\.gr.+epikairothta/a8lhtismos/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_kathimerini', follow=True ,process_request='process_kathimerini'), 
        Rule(LinkExtractor(allow=(r"\.tovima\.gr.+sports"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tovima', follow=True ,process_request='process_tovima'), 
        Rule(LinkExtractor(allow=(r"\.tanea\.gr.+sports"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tanea', follow=True ,process_request='process_tanea'), 
        Rule(LinkExtractor(allow=('iefimerida.gr/spor'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_iefimerida', follow=True ,process_request='process_iefimerida'), 
        Rule(LinkExtractor(allow=(r"gaz.+/football/",r"gaz.+/basketball/",r"gaz.+/other-sports/",r"gaz.+/volleyball/",r"gaz.+/tennis/",), deny=('power-rankings/')), callback='parse_gazzetta', follow=True ,process_request='process_gazzeta'),    
        Rule(LinkExtractor(allow=('sport24.gr/football/','sport24.gr/sports/','sport24.gr/Basket/'), deny=('vid','gallery','pic')),callback='parse_sport24', follow=True ,process_request='process_sport24'),
        Rule(LinkExtractor(allow=('cnn.gr/sports')),callback='parse_cnn', follow=True ,process_request='process_cnn'),
        Rule(LinkExtractor(allow=('reader.gr/athlitismos'), deny=('vid')), callback='parse_reader_crawl', follow=True ,process_request='process_reader'),
        Rule(LinkExtractor(allow=('thetoc.gr/athlitika'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_thetoc', follow=True ,process_request='process_thetoc'),
        Rule(LinkExtractor(allow=('protagon.gr/epikairotita/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_protagon', follow=True ,process_request='process_protagon'),
        Rule(LinkExtractor(allow=(r"\.in\.gr.+/sports/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_in', follow=True ,process_request='process_in'), 
        Rule(LinkExtractor(allow=('newpost.gr/athlitika/'), deny=('page')), callback='parse_newpost', follow=True ,process_request='process_newpost'),
        Rule(LinkExtractor(allow=('periodista.gr/athlhtika-paraskhnia'), deny=('start=')), callback='parse_periodista', follow=True ,process_request='process_periodista'), 
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
            list_to_string = " ".join(text)
            no_spaces_text = re.findall(r'[/<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
            final_text = " ".join(no_spaces_text)
            clear_characters = re.sub( "\xa0"," ",final_text)

            date = response.xpath('//time[@class="entry-date published"]/text()').get()
            final_date = formatdate(date)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            #check if we are in an article, and if it doesn't have images
            if len(final_text)>10 and flag is None:
                newsit_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['SPORT'],
                    "subtopic": GENERAL_CATEGORIES['SPORT'],
                    "website": NEWSIT_VARS['WEBSITE'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": NEWSIT_VARS['WEBSITE'],
                    "article_body": clear_characters,
                    "url": url,                
                }  

    def process_newsit(self, request):
        global newsit_counter
        if newsit_counter < 300:
            return request  

    #function for items from sport24
    def parse_sport24(self,response):
        global sport24_counter
        #check if we are in an articles url
        title = response.xpath('//div[@class="storyContent"]/h1/text()').get()
        if title is not None and sport24_counter < 300:
            #get article's text
            text = response.xpath('//div[@itemprop="articleBody"]//p/text()|//div[@itemprop="articleBody"]//h3/text()|//div[@itemprop="articleBody"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)
            clear_escape = re.sub(r'\n|\t',"",clear_characters)

            date = response.xpath('//span[@class="byline_date"]/b/text()').get()
            fix_date = re.search(r"(\d+).(\w+)\..(\d+)",date).group(0)
            nodot_date = re.sub(r"\.","",fix_date)
            final_date = formatdate(nodot_date)

            #flag to see later on if we have tweets ect
            #flag = re.search(r"@",clear_escape)
            url = response.url
            subtopic = url.split('/')[3]
            sport24_counter += 1
            yield {
                "topic": GENERAL_CATEGORIES['SPORT'],
                "subtopic": subtopic,
                "website" : SPORT24_VARS['WEBSITE'],
                "title": title,
                "article_date": final_date,
                "author": response.xpath('//span[@class="byline_author"]/b/text()').get(),
                "article_body": clear_escape, 
                "url": url
            }

    def process_sport24(self, request):
        global sport24_counter
        if sport24_counter < 300:
            return request

    #function for items from gazzetta
    def parse_gazzetta(self, response):
        global gazzetta_counter
        #check if we are in an articles url
        title = response.xpath('//div[@class="field-item even"]/h1/text()').get()
        if title is not None and gazzetta_counter < 300:
            # extract subtitle by splitting our url by '/'
            # and keeping the third object on our created list
            url = response.url
            subtopic = url.split('/')[3]

            temp=response.xpath('//span[@itemprop="name"]/text()').get()
            #check if there is an author
            if isinstance(temp,str):
                author = re.fullmatch(r'\W+',temp)
                if author is None:
                    author = temp
                else:
                    author = GAZZEETTA_VARS['WEBSITE']
            elif author is None:
                author = response.xpath('//h3[@class="blogger-social"]/a/text()').get()
            else:
                author = GAZZEETTA_VARS['WEBSITE']

            date = response.xpath('//div[@class="article_date"]/text()').get()
            final_date = formatdate(date)

            text = response.xpath('//div[@itemprop="articleBody"]//p/text()|//p/a/text()|//p/strong/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)
            clear_escape = re.sub(r'\n|\t',"",clear_characters)

            flag = re.search(r"@",clear_escape)
            if flag is None:
                gazzetta_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['SPORT'],
                    "subtopic": subtopic,
                    "website": GAZZEETTA_VARS['WEBSITE'],
                    "title": title,
                    "article_date": final_date,
                    "author": author,
                    "article_body": clear_escape ,
                    "url": url
                }

    def process_gazzeta(self, request):
        global gazzetta_counter
        if gazzetta_counter < 300:
            return request

#function for cnn crawl
    def parse_cnn(self,response):
        global cnn_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@class="main-title"]/text()').get() 
        if title is not None and cnn_counter <300:
            cnn_counter += 1
            text = response.xpath('//div[@class="main-content story-content"]//p/text()|//div[@class="main-content story-content"]//strong/text()|//div[@class="main-content story-content"]//a/text()').getall()
            list_to_string = " ".join(text)
            no_spaces_text = re.findall(r'[/<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
            final_text = " ".join(no_spaces_text)
            clear_characters = re.sub( "\xa0"," ",final_text)

            date = re.sub(r'\n|\t',"",response.xpath('//time/text()').get())
            final_date = formatdate(date)

            url = response.url
            yield {
                "topic": GENERAL_CATEGORIES['SPORT'],
                "subtopic": GENERAL_CATEGORIES['SPORT'],
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

    #the next two functions needed to crawl reader.gr
    def parse_reader_crawl(self,response):
        links = response.xpath('//h1[@class="article-title"]/a/@href|//div[@class="row region"]').getall()
        for link in links:
            if len(link) < READER_VARS['MAX_LINKS']:
                url = response.urljoin(link)
                yield Request(url,callback=self.parse_reader_item)


    def parse_reader_item(self,response):
        global reader_counter
        #check if we are in an articles url
        title = response.xpath('//h1/text()').get() 
        if title is not None and reader_counter < 300:
            #get article's text
            text = response.xpath('//div[@class="article-body ads-in"]//p/text()|//div[@class="article-body ads-in"]//p/text()|//div[@class="article-body ads-in"]//p/*/text()').getall()
            list_to_string = " ".join(text)
            no_spaces_text = re.findall(r'[/<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
            final_text = " ".join(no_spaces_text)
            clear_characters = re.sub( "\xa0"," ",final_text)

            date = response.xpath('//time/text()').get()
            final_date = formatdate(date)

            author = response.xpath('//p[@class="article-author"]/a/text()').get()
            if author is not None:
                author = re.sub("\xa0","",author)
            else:
                author = READER_VARS['AUTHOR']

            url = response.url
            if title is not None:
                reader_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['SPORT'],
                    "subtopic": GENERAL_CATEGORIES['SPORT'],
                    "website": READER_VARS['AUTHOR'],
                    "title": re.sub( r'\n|\t',"",title),
                    "article_date": final_date,
                    "author": author,
                    "article_body": clear_characters,
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
            #get article's text
            text = response.xpath('//div[@class="article-content articleText"]//p/text()|//div[@class="article-content articleText"]//strong/text()|//div[@class="article-content articleText"]//p/*/text()').getall()
            list_to_string = " ".join(text)
            text = re.findall(r'[<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
            final_text = " ".join(text)
            clear_characters = re.sub( "\xa0"," ",final_text)

            date = response.xpath('//span[@class="article-date"]/text()').get()
            final_date = THETOC_VARS['full_date'] +formatdate(date)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            #check if we are in an article and that it doesn't have images
            if len(text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                thetoc_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['SPORT'],
                    "subtopic": GENERAL_CATEGORIES['SPORT'],
                    "website": THETOC_VARS['WEBSITE'],
                    "title": title,
                    "article_date": final_date,
                    "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="author-social"]//h5/a/span[2]/text()').get()),
                    "article_body": clear_characters,
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
        if title is not None and protagon_counter < 300:
            sub = response.xpath('//span[@class="s_roumpr"]/a/text()').get()
            if sub == GENERAL_CATEGORIES['SPORT']:
                #get article's text
                text = response.xpath('//div[@class="left-single-column "]//p/text()|//div[@class="left-single-column "]//strong/text()|//div[@class="left-single-column "]//p/*/text()').getall()
                list_to_string = " ".join(text)
                no_spaces_text = re.findall(r'[/<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
                final_text = " ".join(no_spaces_text)
                clear_characters = re.sub( "\xa0"," ",final_text)

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)

                author = re.findall(r"(\w+).(\w+)",response.xpath('//strong[@class="generalbold uppercase"]/a/text()').get())
                list_to_tuple = author[0]
                author = ' '.join(list_to_tuple)

                date = response.xpath('//span[@class="generalight uppercase"]/text()').get()
                final_date = formatdate(date)

                url = response.url
                #check if we are in an article and that it doesn't have images
                if len(text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    protagon_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['SPORT'],
                        "subtopic": sub,
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

    def parse_in(self,response):
        global in_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@class="headine"]/text()').get() 
        if title is not None and in_counter < 300 :
            text = response.xpath('//div[@class="main-content pos-rel article-wrapper prel"]//p/text()|//div[@class="main-content pos-rel article-wrapper prel"]//strong/text()|//div[@class="main-content pos-rel article-wrapper prel"]//p/*/text()').getall()
            list_to_string = " ".join(text)
            no_spaces_text = re.findall(r'[/<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
            final_text = " ".join(no_spaces_text)
            clear_characters = re.sub( "\xa0"," ",final_text)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            date = response.xpath('//time/text()').get()
            final_date = formatdate(date)

            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                in_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['SPORT'],
                    "subtopic": GENERAL_CATEGORIES['SPORT'],
                    "website": IN_VARS['WEBSITE'],
                    "title": title,
                    "article_date": final_date, 
                    "author": response.xpath('//div[@class="author-name"]//a/text()').get(),
                    "article_body": clear_characters,
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
            list_to_string = " ".join(text)
            no_spaces_text = re.findall(r'[/<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
            final_text = " ".join(no_spaces_text)
            clear_characters = re.sub( "\xa0"," ",final_text)
            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            date = (response.xpath('//small[@class="article-created-time"]/text()').get()).split('/')[0]
            final_date = formatdate(date)

            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                newpost_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['SPORT'],
                    "subtopic": GENERAL_CATEGORIES['SPORT'],
                    "website": NEWPOST_VARS['WEBSITE'],
                    "title": title,
                    "article_date": final_date, 
                    "author": NEWPOST_VARS['WEBSITE'],
                    "article_body": clear_characters,
                    "url": url,                
            }

    def process_newpost(self, request):
        global newpost_counter
        if newpost_counter < 300:
            return request

    def parse_periodista(self,response):
        global periodista_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@itemprop="headline"]/text()').get() 
        if title is not None and periodista_counter < 300:
            #get article's text
            text = response.xpath('//div[@class="per-item-page-part per-article-body"]//p/text()|//div[@class="per-item-page-part per-article-body"]//strong/text()|//div[@class="per-item-page-part per-article-body"]//p/*/text()').getall()
            list_to_string = " ".join(text)
            text = re.findall(r'[<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
            final_text = " ".join(text)
            clear_characters = re.sub( "\xa0"," ",final_text)
            url = response.url

            date = response.xpath('//div[@class="col-md-4 per-color-grey per-font-size-md per-padding-top-20"]/text()').get()
            final_date = formatdate(date)

            #flag to see later on if we have videos
            flag = re.search(r"binteo|foto",url)

            #check if we are in an article, and if it doesn't have videos
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                periodista_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['SPORT'],
                    "subtopic": GENERAL_CATEGORIES['SPORT'],
                    "website": PERIODISTA_VARS['WEBSITE'],
                    "title": re.sub( r'\t|\n|\r',"",title),
                    "article_date": final_date,  
                    "author": PERIODISTA_VARS['WEBSITE'],
                    "article_body": clear_characters,
                    "url": url,                
                } 

    def process_periodista(self, request):
        global periodista_counter
        if periodista_counter < 300:
            return request

    def parse_iefimerida(self,response):
        global iefimerida_counter
        #check if we are in an articles url
        title = response.xpath('//h1/span/text()').get() 
        if title is not None and iefimerida_counter < 300:
            #get article's text
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
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                iefimerida_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['SPORT'],
                    "subtopic": GENERAL_CATEGORIES['SPORT'],
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
            list_to_string = " ".join(text)
            no_spaces_text = re.findall(r'[/<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
            final_text = " ".join(no_spaces_text)
            clear_characters = re.sub( "\xa0"," ",final_text)

            date = response.xpath('//span[@class="firamedium postdate updated"]/text()').get()
            final_date = formatdate(date)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)

            #get subtopic from url
            url = response.url
            subtopic = url.split('/')[7]
            if len(subtopic)>TANEA_VARS['SUBTOPIC_LENGTH_ALLOWED'] :
                subtopic = GENERAL_CATEGORIES['SPORT']
            
            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                tanea_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['SPORT'],
                    "subtopic": subtopic,
                    "website": TANEA_VARS['AUTHOR'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": TANEA_VARS['AUTHOR'],
                    "article_body": clear_characters,
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
            list_to_string = " ".join(text)
            text = re.findall(r'[<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
            final_text = " ".join(text)
            clear_characters = re.sub("\xa0"," ",final_text)

            date = response.xpath('//time/span/text()').get()
            final_date = formatdate(date)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            
            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                tovima_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['SPORT'],
                    "subtopic": GENERAL_CATEGORIES['SPORT'],
                    "website": TOVIMA_VARS['AUTHOR'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": TOVIMA_VARS['AUTHOR'],
                    "article_body": clear_characters,
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
        if title is not None and kathimerini_counter < 300:
            #fix title's format
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            #get article's text
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
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None: 
                kathimerini_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['SPORT'],
                    "subtopic": GENERAL_CATEGORIES['SPORT'],
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
        if title is not None and naftemporiki_counter < 300:
            #check if we are in the correct category
            subtopic = response.xpath('//span[@itemprop="articleSection"]/text()').get()
            if subtopic == NAFTEMPORIKI_VARS['CATEGORY_SPORT'] :
                #fix title's format
                list_to_string = " ".join(" ".join(title))
                markspaces = re.sub( "       ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                put_spaces_back = re.sub( "space", " ",uneeded_spaces)
                final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

                #get article's text
                text = response.xpath('//div[@class="entityMain article"]//p/text()|//div[@class="entityMain article"]/p/strong/text()|//div[@class="entityMain article"]//h3/text()|//div[@class="entityMain article"]//p/*/text()').getall()
                list_to_string = " ".join(text)
                text = re.findall(r'[<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
                final_text = " ".join(text)
                clear_characters = re.sub( "\xa0"," ",final_text)

                date = response.xpath('//div[@class="Date"]/text()').get()
                final_date = formatdate(date)

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url
                
                #check if we are in an article and that it doesn't have images
                if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    naftemporiki_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['SPORT'],
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

    def parse_popaganda(self,response):
        global popaganda_counter
        #check if we are in an articles url
        title = response.xpath('//h1/text()').get()
        if title is not None and popaganda_counter < 300:
            #check if we are in the correct category
            category = response.xpath('//div[@class="category"]/a/text()').get()
            if category == POPAGANDA_VARS['CATEGORY_SPORT']:
                #fix title's format
                list_to_string = " ".join(" ".join(title))
                markspaces = re.sub( "       ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                put_spaces_back = re.sub( "space", " ",uneeded_spaces)
                final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

                #get article's text
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
                if title is not None and len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    popaganda_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['SPORT'],
                        "subtopic": POPAGANDA_VARS['SPORT'],
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
        if title is not None and topontiki_counter < 300:
            #check if we are in the correct category
            sub = response.xpath('//h2/a/text()').get()
            if sub == TOPONTIKI_VARS['CATEGORY_SPORT']:
                #fix title's format
                list_to_string_title = "".join(title) 

                #get article's text
                text = response.xpath('//div[@class="field-item even"]//p/text()|//div[@class="field-item even"]//p/*/text()|//div[@class="field-item even"]//p//span/text()').getall()
                list_to_string = " ".join(text)
                text = re.findall(r'[<>«»();":\\\'\-,\.0-9a-zA-Z\u0370-\u03ff\u1f00-\u1fff]+',list_to_string)
                final_text = " ".join(text)
                clear_characters = final_text.replace("\xa0","")

                date = response.xpath('//span[@class="date"]/text()').get()
                final_date = formatdate(date)

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url
                
                #check if we are in an article and that it doesn't have images
                if title is not None and len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    topontiki_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['SPORT'],
                        "subtopic": GENERAL_CATEGORIES['SPORT'],
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
