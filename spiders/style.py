# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item
from news2.settings import IEFIMERIDA_VARS,TANEA_VARS,LIFO_VARS,NEWPOST_VARS
from news2.settings import CNN_VARS,GENERAL_CATEGORIES,IN_VARS

class DogSpider(CrawlSpider):
    name = 'style'
    allowed_domains = [
        'lifo.gr',
        'tanea.gr',
        'cnn.gr',
        'thetoc.gr',
        'in.gr',
        'newpost.gr',
        'iefimerida.gr',
        ]
    url = [
        'https://www.cnn.gr/style/politismos',
        'https://www.thetoc.gr/',
        'https://www.in.gr/'
        'https://newpost.gr/lifestyle',
        'https://www.iefimerida.gr',
        ]
    lifo_urls = ['https://www.lifo.gr/articles/design_articles']+['https://www.lifo.gr/articles/fashion_articles']+['https://www.lifo.gr/now/people/page:{}'.format(x) for x in range(1,LIFO_VARS['PEOPLE_PAGES'])]
    newpost_urls = ['http://newpost.gr/lifestyle?page={}'.format(x) for x in range(1,NEWPOST_VARS['STYLE_PAGES'])]
    tanea_urls = ['https://www.tanea.gr/category/woman/page/{}'.format(x) for x in range(1,TANEA_VARS['WOMEN_PAGES'])]
    urls = url + newpost_urls + tanea_urls + lifo_urls
    start_urls = urls[:]

    rules = (
        Rule(LinkExtractor(allow=(r'www\.lifo\.gr.+design_articles/'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_lifo', follow=True), 
        Rule(LinkExtractor(allow=(r'www\.lifo\.gr.+people/'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_lifo', follow=True), 
        Rule(LinkExtractor(allow=(r'www\.lifo\.gr.+woman_articles'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_lifo', follow=True),
        Rule(LinkExtractor(allow=('https://www.iefimerida.gr/design|https://www.iefimerida.gr/gynaika'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_iefimerida', follow=True), 
        Rule(LinkExtractor(allow=('/politismos/'),deny=('gallery')), callback='parse_infinite_cnn', follow=True), 
        Rule(LinkExtractor(allow=('thetoc.gr/people-style'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_thetoc', follow=True),
        Rule(LinkExtractor(allow=(r"\.in\.gr.+/health/|\.in\.gr.+/life/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_in', follow=True),
        Rule(LinkExtractor(allow=('newpost.gr/lifestyle'), deny=()), callback='parse_newpost', follow=True), 
        )

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
        if article_type == CNN_VARS['ARTICLE_TYPE'] and contains_photos is None:
            yield{ 
                "subtopic": GENERAL_CATEGORIES['STYLE'],
                "website": CNN_VARS['WEBSITE'],
                "title": title,
                "date": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get()),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-author"]/text()').get()),
                "text": re.sub( r'\n|\t',"",final_text),
                "url": url,     
            }

    def parse_thetoc(self,response):
        #check if we are in an articles url
        title = response.xpath('//div[@class="article-title"]//h1/text()').get() 
        if title is not None:
            #get article's text
            text = response.xpath('//div[@class="article-content articleText"]//p/text()|//div[@class="article-content articleText"]//strong/text()|//div[@class="article-content articleText"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": GENERAL_CATEGORIES['STYLE'],
                    "website": re.search(r"www.+\.gr",url).group(0),
                    "title": title,
                    "date": " ".join(re.findall(r"[0-9]+.[α-ωΑ-Ω]+\..[0-9]+",response.xpath('//span[@class="article-date"]/text()').get())),
                    "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="author-social"]//h5/a/span[2]/text()').get()),
                    "text": re.sub( r'\n|\t',"",clear_characters),
                    "url": url,                
                }

    def parse_in(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@class="entry-title black-c"]/text()').get() 
        if title is not None:
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

            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": IN_VARS['STYLE_SUBTOPIC'],
                    "website": IN_VARS['WEBSITE'],
                    "title": title,
                    "date": response.xpath('//time/text()').get(), 
                    "author": response.xpath('//span[@class="vcard author"]//a/text()').get(),
                    "text": re.sub( r'\s\s\s',"",clear_characters),
                    "url": url,                
                }

    def parse_newpost(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@class="article-title"]/text()').get() 
        if title is not None:
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

            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": NEWPOST_VARS['STYLE_SUBTOPIC'],
                    "website": NEWPOST_VARS['WEBSITE'],
                    "title": title,
                    "date": (response.xpath('//small[@class="article-created-time"]/text()').get()).split('/')[0], 
                    "author": NEWPOST_VARS['WEBSITE'],
                    "text": re.sub( r'\s\s\s',"",clear_characters),
                    "url": url,                
            }

    def parse_iefimerida(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1/span/text()').get() 
        if title is not None:
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

            #check if we are in an article and that it doesn't have images
            if title is not None and len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": subtopic,
                    "website": IEFIMERIDA_VARS['AUTHOR'],
                    "title": title,
                    "date": re.sub(r"\|"," ",re.search(r"(\d+)\|(\d+)\|(\d+)",response.xpath('//span[@class="created"]/text()').get()).group(0)), 
                    "author": IEFIMERIDA_VARS['AUTHOR'],
                    "text": re.sub( r'\s\s\s|\n',"",clear_characters),
                    "url": url,                
                }

    def parse_tanea(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@class="entry-title black-c"]/text()').get() 
        if title is not None:
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

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            
            #check if we are in an article and that it doesn't have images
            if title is not None and len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": TANEA_VARS['CATEGORY_STYLE'],
                    "website": TANEA_VARS['AUTHOR'],
                    "title": final_title,
                    "date": response.xpath('//span[@class="firamedium postdate updated"]/text()').get(), 
                    "author": TANEA_VARS['AUTHOR'],
                    "text": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                }

    def parse_lifo(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@itemprop="headline"]/text()|//meta[@itemprop="headline"]/text()|//h1/*/text()').get() 
        if title is not None:
            #fix title's format
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

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
                yield {
                    "subtopic": subtopic,
                    "website": LIFO_VARS['AUTHOR'],
                    "title": final_title,
                    "date": response.xpath('//time/text()').get(), 
                    "author": author,
                    "text": re.sub( r'\s\s\s|\n',"",clear_characters),
                    "url": url,                
                }