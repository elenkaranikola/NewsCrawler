# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item
from news2.settings import PERIODISTA_VARS,PRESSPROJECT_VARS,IEFIMERIDA_VARS,TANEA_VARS
from news2.settings import TOVIMA_VARS,NAFTEMPORIKI_VARS,EFSYN_VARS,READER_VARS
from news2.settings import TOPONTIKI_VARS,GENERAL_CATEGORIES, NEWPOST_VARS
from news2.settings import PROTAGON_VARS


class DogSpider(CrawlSpider):
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
        'thepressproject.gr',
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
        'https://www.thepressproject.gr/',
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
        Rule(LinkExtractor(allow=('topontiki.gr/article/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_topontiki', follow=True), 
        Rule(LinkExtractor(allow=(r'www\.efsyn\.gr.+node/'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_efsyn', follow=True), 
        Rule(LinkExtractor(allow=(r"\.naftemporiki\.gr.+finance/story"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_naftemporiki', follow=True), 
        Rule(LinkExtractor(allow=(r"\.tovima\.gr.+finance"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tovima', follow=True), 
        Rule(LinkExtractor(allow=(r"\.tanea\.gr.+economy"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tanea', follow=True),
        Rule(LinkExtractor(allow=('iefimerida.gr/oikonomia'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_iefimerida', follow=True), 
        Rule(LinkExtractor(allow=('thepressproject'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_thepressproject', follow=True), 
        Rule(LinkExtractor(allow=('periodista.gr/oikonomia'), deny=()), callback='parse_periodista', follow=True),
        Rule(LinkExtractor(allow=('cnn.gr/oikonomia'), deny=('cnn.gr/oikonomia/gallery/')), callback='parse_cnn', follow=True), 
        Rule(LinkExtractor(allow=('reader.gr/news/oikonomia'), deny=('vid')), callback='parse_reader', follow=True),
        Rule(LinkExtractor(allow=('thetoc.gr/oikonomia'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_thetoc', follow=True),
        Rule(LinkExtractor(allow=('protagon.gr/epikairotita/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_protagon', follow=True),
        Rule(LinkExtractor(allow=(r"\.in\.gr.+/economy/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_in', follow=True), 
        Rule(LinkExtractor(allow=('newpost.gr/oikonomia'), deny=()), callback='parse_newpost', follow=True), 
        )

    def parse_cnn(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@class="story-title"]/text()').get() 
        if title is not None :

            text = response.xpath('//div[@class="story-content"]//p/text()|//div[@class="story-content"]//strong/text()|//div[@class="story-content"]//a/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            url = response.url
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH']:
                yield {
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
                    "website": re.search(r"www.+\.gr",url).group(0),
                    "title": title,
                    "date": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get()),
                    "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-author"]/text()').get()),
                    "text": re.sub( r'\n|\t',"",clear_characters),
                    "url": url,                
                }

    def parse_reader(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1/text()').get() 
        if title is not None:

            text = response.xpath('//div[@class="article-summary"]//p/text()|//div[@class="article-body"]//p/text()|//div[@class="article-body"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            author = response.xpath('//p[@class="article-author"]/a/text()').get()
            if author is not None:
                author = re.sub("\xa0","",author)
            else:
                author = READER_VARS['AUTHOR']

            url = response.url
            yield {
                "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": re.sub( r'\n|\t',"",title),
                "date": re.sub( r'\n|\t',"",response.xpath('//time/text()').get()),
                "author": author,
                "text": re.sub( r'\n|\t',"",clear_characters),
                "url": url,              
            }

    def parse_thetoc(self,response):
        #check if we are in an articles url
        title = response.xpath('//div[@class="article-title"]//h1/text()').get() 
        if title is not None:

            text = response.xpath('//div[@class="article-content articleText"]//p/text()|//div[@class="article-content articleText"]//strong/text()|//div[@class="article-content articleText"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            url = response.url
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH']:
                yield {
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
                    "website": re.search(r"www.+\.gr",url).group(0),
                    "title": title,
                    "date": " ".join(re.findall(r"[0-9]+.[α-ωΑ-Ω]+\..[0-9]+",response.xpath('//span[@class="article-date"]/text()').get())),
                    "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="author-social"]//h5/a/span[2]/text()').get()),
                    "text": re.sub( r'\n|\t',"",clear_characters),
                    "url": url,                
                }

    def parse_protagon(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@class="entry-title"]/text()').get()
        if title is not None :
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

                date = re.findall(r"(\d+).(\w+).(\d+)",response.xpath('//span[@class="generalight uppercase"]/text()').get())
                list_to_tuple = date[0]
                date = ' '.join(list_to_tuple)

                #check if we are in an article and that it doesn't have images
                if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    yield {
                        "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
                        "website": re.search(r"www.+\.gr",url).group(0),
                        "title": title,
                        "date": date, 
                        "author": author,
                        "text": re.sub( r'\s\s\s',"",clear_characters),
                        "url": url,                
                    }

    def parse_periodista(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@itemprop="headline"]/text()').get() 
        if title is not None:
            text = response.xpath('//div[@class="per-item-page-part per-article-body"]//p/text()|//div[@class="per-item-page-part per-article-body"]//strong/text()|//div[@class="per-item-page-part per-article-body"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            #flag to see later on if we have videos
            url = response.url
            flag = re.search(r"binteo|foto",url)

            #check if we are in an article and that it doesn't have videos
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
                    "website": re.search(r"www.+\.gr",url).group(0),
                    "title": re.sub( r'\t|\n|\r',"",title),
                    "date": re.sub(r'\t|\n|\r',"",response.xpath('//div[@class="col-md-4 per-color-grey per-font-size-md per-padding-top-20"]/text()').get()), 
                    "author": "periodista.gr",
                    "text": re.sub( r'\s\s\s',"",clear_characters),
                    "url": url,                
                }  

            

    def parse_in(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@class="entry-title black-c"]/text()').get() 
        if title is not None:

            text = response.xpath('//div[@class="main-content pos-rel article-wrapper"]//p/text()|//div[@class="main-content pos-rel article-wrapper"]//strong/text()|//div[@class="main-content pos-rel article-wrapper"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            #check if we are in an article and that it doesn't have any images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
                    "website": re.search(r"www.+\.gr",url).group(0),
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

            text = response.xpath('//div[@class="article-main clearfix"]//p/text()|//div[@class="article-main clearfix"]//strong/text()|//div[@class="article-main clearfix"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            #check if we are in an article and that it doesn't have any images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
                    "website": NEWPOST_VARS['WEBSITE'],
                    "title": title,
                    "date": (response.xpath('//small[@class="article-created-time"]/text()').get()).split('/')[0], 
                    "author": NEWPOST_VARS['WEBSITE'],
                    "text": re.sub( r'\s\s\s',"",clear_characters),
                    "url": url,                
            }

    def parse_thepressproject(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@class="entry-title"]/text()|//h1[@class="entry-title"]/*/text()').get()
        if title is not None:
            #check if we are in the correct category
            sub = response.xpath('//div[@class="article-categories"]/a/text()').get()
            if sub == PRESSPROJECT_VARS['CATEGORY_ECONOMICS']:
                #check if this is a video article
                video_article = response.xpath('//i[@class="title-icon video-icon fab fa-youtube"]').get()
                if video_article is None:
                    list_to_string = " ".join(" ".join(title))
                    no_whites = re.sub(r'\t|\n',"",list_to_string)
                    markspaces = re.sub( "       ", "space",no_whites)
                    uneeded_spaces = re.sub( " ", "",markspaces)
                    final_title = re.sub( "space", " ",uneeded_spaces)
                    delete_front_space = re.sub("    ","",final_title)
                    final_title = re.sub("   ","",delete_front_space)

                    text = response.xpath('//div[@id="maintext"]//p/text()|//div[@id="maintext"]//strong/text()|//div[@id="maintext"]//p/*/text()').getall()
                    list_to_string = " ".join(" ".join(text))
                    markspaces = re.sub( "  ", "space",list_to_string)
                    uneeded_spaces = re.sub( " ", "",markspaces)
                    final_text = re.sub( "space", " ",uneeded_spaces)
                    clear_characters = re.sub( "\xa0","",final_text)

                    #flag to see later on if we have tweets ect
                    flag = re.search(r"@",clear_characters)
                    url = response.url
                    date = response.xpath('//div[@class="article-date"]/label[1]/text()').get()

                    #check if we are in an article and that it doesn't have any images
                    if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                        yield {
                            "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
                            "website": PRESSPROJECT_VARS['AUTHOR'],
                            "title": final_title,
                            "date": date, 
                            "author": PRESSPROJECT_VARS['AUTHOR'],
                            "text": re.sub( r'\s\s\s',"",clear_characters),
                            "url": url,                
                        }
                
    def parse_iefimerida(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1/span/text()').get() 
        if title is not None:

            text = response.xpath('//div[@class="field--name-body on-container"]//p/text()|//div[@class="field--name-body on-container"]/strong/text()|//div[@class="field--name-body on-container"]//p/*/text()|//div[@class="field--name-body on-container"]//p//li/text()').getall()
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
                yield {
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
                    "website": IEFIMERIDA_VARS['AUTHOR'],
                    "title": title,
                    "date": re.sub(r"\|"," ",re.search(r"(\d+)\|(\d+)\|(\d+)",response.xpath('//span[@class="created"]/text()').get()).group(0)), 
                    "author": IEFIMERIDA_VARS['AUTHOR'],
                    "text": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                }
            
    def parse_tanea(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@class="entry-title black-c"]/text()').get() 
        if title is not None:
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

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            #check if we are in an article and that it doesn't have any images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
                    "website": TANEA_VARS['AUTHOR'],
                    "title": final_title,
                    "date": response.xpath('//span[@class="firamedium postdate updated"]/text()').get(), 
                    "author": TANEA_VARS['AUTHOR'],
                    "text": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                }

    def parse_tovima(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@class="entry-title thirty black-c zonabold"]/text()').get() 
        if title is not None:
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

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            
            #check if we are in an article and that it doesn't have any images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
                    "website": TOVIMA_VARS['AUTHOR'],
                    "title": final_title,
                    "date": response.xpath('//time/span/text()').get(), 
                    "author": TOVIMA_VARS['AUTHOR'],
                    "text": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                }

    def parse_naftemporiki(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@id="sTitle"]/text()').get() 
        if title is not None:
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

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
                yield {
                    "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
                    "website": NAFTEMPORIKI_VARS['AUTHOR'],
                    "title": final_title,
                    "date": response.xpath('//div[@class="Date"]/text()').get(), 
                    "author": NAFTEMPORIKI_VARS['AUTHOR'],
                    "text": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                } 

    def parse_efsyn(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[1]/text()').get() 
        if title is not None:
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
                
                #check if we are in an article and that it doesn't have any images
                if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    yield {
                        "subtopic": EFSYN_VARS['ECONOMICS'],
                        "website": EFSYN_VARS['WEBSITE'],
                        "title": final_title,
                        "date": response.xpath('//time/text()').get(), 
                        "author": author,
                        "text": re.sub( r'\s\s\s|\n',"",clear_characters),
                        "url": url,                
                    }

    def parse_topontiki(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1/text()').get()
        if title is not None:
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

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url
                
                #check if we are in an article and that it doesn't have any images
                if title is not None and len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    yield {
                        "subtopic": GENERAL_CATEGORIES['ECONOMICS'],
                        "website": TOPONTIKI_VARS['WEBSITE'],
                        "title": final_title,
                        "date": response.xpath('//span[@class="date"]/text()').get(), 
                        "author": TOPONTIKI_VARS['WEBSITE'],
                        "text": re.sub( r'\s\s\s|\n',"",clear_characters),
                        "url": url,                
                    }