# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from NewsCrawler.utilities import formatdate
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from NewsCrawler.items import NewsCrawlerItem
from NewsCrawler.settings import IEFIMERIDA_VARS,TANEA_VARS,LIFO_VARS,NEWPOST_VARS
from NewsCrawler.settings import CNN_VARS,GENERAL_CATEGORIES,IN_VARS,THETOC_VARS
from NewsCrawler.settings import NEWSIT_VARS
import mysql.connector

newsit_counter = 0
lifo_counter = 0
tanea_counter = 0
cnn_counter = 0
thetoc_counter = 0
in_counter = 0
newpost_counter = 0
iefimerida_counter = 0

class StyleSpider(CrawlSpider):
    name = 'style'
    allowed_domains = [
        'newsit.gr',
        'lifo.gr',
        'tanea.gr',
        'cnn.gr',
        'thetoc.gr',
        'in.gr',
        'newpost.gr',
        'iefimerida.gr',
        ]
    url = [
        'https://www.newsit.gr/category/lifestyle/',
        'https://www.cnn.gr/style/moda',
        'https://www.thetoc.gr/people-style',
        'https://www.in.gr/life/'
        'https://newpost.gr/lifestyle',
        'https://www.iefimerida.gr',
        ]
    lifo_urls = ['https://www.lifo.gr/articles/design_articles']+['https://www.lifo.gr/articles/fashion_articles']+['https://www.lifo.gr/now/people/page:{}'.format(x) for x in range(1,LIFO_VARS['PEOPLE_PAGES'])]
    newpost_urls = ['http://newpost.gr/lifestyle?page={}'.format(x) for x in range(1,NEWPOST_VARS['STYLE_PAGES'])]
    tanea_urls = ['https://www.tanea.gr/category/woman/page/{}'.format(x) for x in range(1,TANEA_VARS['WOMEN_PAGES'])] +['https://www.tanea.gr/category/kid/page/{}'.format(x) for x in range(1,TANEA_VARS['CHILD_PAGES'])]
    
    urls = url + newpost_urls + tanea_urls + lifo_urls
    start_urls = urls[:]

    rules = (
        Rule(LinkExtractor(allow=(r"\.tanea\.gr.+kid",r"\.tanea\.gr.+woman"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tanea', follow=True ,process_request='process_tanea'), 
        Rule(LinkExtractor(allow=(r"\.newsit\.gr.+lifestyle/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_newsit', follow=True ,process_request='process_newsit'), 
        Rule(LinkExtractor(allow=(r'www\.lifo\.gr.+design_articles/'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_lifo', follow=True ,process_request='process_lifo'), 
        Rule(LinkExtractor(allow=(r'www\.lifo\.gr.+people/'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_lifo', follow=True, process_request='process_lifo'), 
        Rule(LinkExtractor(allow=(r'www\.lifo\.gr.+woman_articles'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_lifo', follow=True ,process_request='process_lifo'),
        Rule(LinkExtractor(allow=('iefimerida.gr/design','iefimerida.gr/gynaika','iefimerida.gr/zoi','iefimerida.gr/poli'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_iefimerida', follow=True ,process_request='process_iefimerida'), 
        Rule(LinkExtractor(allow=('cnn.gr/style/moda'),deny=('gallery')), callback='parse_infinite_cnn', follow=True ,process_request='process_cnn'), 
        Rule(LinkExtractor(allow=('thetoc.gr/people-style'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_thetoc', follow=True ,process_request='process_thetoc'),
        Rule(LinkExtractor(allow=(r"\.in\.gr.+/health/|\.in\.gr.+/life/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_in', follow=True ,process_request='process_in'),
        Rule(LinkExtractor(allow=(r"newpost.gr/lifestyle/(\w+).+"), deny=('page')), callback='parse_newpost', follow=True ,process_request='process_newpost'), 
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
                    "topic": GENERAL_CATEGORIES['STYLE'],
                    "subtopic": GENERAL_CATEGORIES['STYLE'],
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

#next three functions for cnn infinite scroll for fashion
    def parse_infinite_cnn(self,response):
        pages =  CNN_VARS['CNN_STYLE_PAGES']
        for page in range(0, pages ,9):
            url = 'https://www.cnn.gr/style/moda?start={}'.format(page)
            yield Request(url, callback = self.parse_item_cnn) 

    def parse_item_cnn(self,response):
        links = response.xpath('//h3[@class="item-title"]/a/@href').getall()
        for link in links:
            url = response.urljoin(link)
            yield Request(url,callback=self.parse_item) #"url": response.urljoin(link),

            
    def parse_item(self,response):
        global cnn_counter
        #get article's text
        text = response.xpath('//div[@class="story-content"]//p/text()|//div[@class="story-content"]//strong/text()|//div[@class="story-content"]//a/text()').getall()
        title = response.xpath('//h1[@class="story-title"]/text()').get()
        list_to_string = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        final_text = re.sub( "space", " ",uneeded_spaces)

        url = response.url
        article_type = url.split('/')[5]
        contains_photos = re.search('Photos',final_text)
        #the article isn't a photo gallery

        date = response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get()
        final_date = formatdate(date)

        if article_type == CNN_VARS['ARTICLE_TYPE'] and contains_photos is None and cnn_counter < 300:
            cnn_counter += 1
            yield{ 
                "topic": GENERAL_CATEGORIES['STYLE'],
                "subtopic": GENERAL_CATEGORIES['STYLE'],
                "website": CNN_VARS['WEBSITE'],
                "title": title,
                "article_date": final_date,
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-author"]/text()').get()),
                "article_body": re.sub( r'\n|\t',"",final_text),
                "url": url,     
            }

    def process_cnn(self, request):
        global cnn_counter
        if cnn_counter < 300:
            return request

    def parse_thetoc(self,response):
        global thetoc_counter
        #check if we are in an articles url
        title = response.xpath('//div[@class="article-title"]//h1/text()').get() 
        if title is not None and thetoc_counter < 300:
            #get article's text
            text = response.xpath('//div[@class="article-content articleText"]//p/text()|//div[@class="article-content articleText"]//strong/text()|//div[@class="article-content articleText"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            date = response.xpath('//span[@class="article-date"]/text()').get()
            final_date = THETOC_VARS['full_date'] +formatdate(date)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                thetoc_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['STYLE'],
                    "subtopic": GENERAL_CATEGORIES['STYLE'],
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
                    "topic": GENERAL_CATEGORIES['STYLE'],
                    "subtopic": IN_VARS['STYLE_SUBTOPIC'],
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
            final_date = formatdate(date)

            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                newpost_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['STYLE'],
                    "subtopic": NEWPOST_VARS['STYLE_SUBTOPIC'],
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

            #get subtopic from urls
            url = response.url
            subtopic = url.split('/')[3]

            date = response.xpath('//span[@class="created"]/text()').get()
            final_date = formatdate(date)

            #check if we are in an article and that it doesn't have images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                iefimerida_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['STYLE'],
                    "subtopic": subtopic,
                    "website": IEFIMERIDA_VARS['AUTHOR'],
                    "title": title,
                    "article_date": final_date, 
                    "author": IEFIMERIDA_VARS['AUTHOR'],
                    "article_body": re.sub( r'\s\s\s|\n',"",clear_characters),
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
                    "topic": GENERAL_CATEGORIES['STYLE'],
                    "subtopic": TANEA_VARS['CATEGORY_STYLE'],
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

    def parse_lifo(self,response):
        global lifo_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@itemprop="headline"]/text()|//meta[@itemprop="headline"]/text()|//h1/*/text()').get() 
        if title is not None  and lifo_counter < 300:
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

            author = response.xpath('//div[@class="author"]/a/text()|//div[@itemprop="author"]/*/text()').get()
            if author == None:
                author = LIFO_VARS['AUTHOR']

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            
            #get subtopic
            url = response.url
            subtopic  = response.xpath('//ol/li[3]//span[@itemprop="name"]/text()').get()
            if subtopic == None:
                subtopic = url.split('/')[4]
            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                lifo_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['STYLE'],
                    "subtopic": subtopic,
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