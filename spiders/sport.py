# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from news2.items import News2Item
from news2.settings import PERIODISTA_VARS,IEFIMERIDA_VARS,TANEA_VARS
from news2.settings import TOVIMA_VARS,KATHIMERINI_VARS,NAFTEMPORIKI_VARS
from news2.settings import POPAGANDA_VARS,TOPONTIKI_VARS,GENERAL_CATEGORIES
from news2.settings import NEWPOST_VARS,SPORT24_VARS,GAZZEETTA_VARS,CNN_VARS
from news2.settings import NEWPOST_VARS,READER_VARS,IN_VARS


class SportSpider(CrawlSpider):
    name = 'sport'
    allowed_domains = [
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
        'https://popaganda.gr/newstrack/sports/',
        'https://www.naftemporiki.gr/sports',
        'https://www.tanea.gr',
        'https://www.iefimerida.gr',
        'http://www.gazzetta.gr/',
        'https://www.sport24.gr',
        'https://www.cnn.gr',
        'https://www.reader.gr/athlitismos',
        'https://www.thetoc.gr/',
        'https://www.protagon.gr/epikairotita/',
        'https://www.in.gr/sports/',
        'https://newpost.gr/athlitika',
        ]
    topontiki_urls = ['http://www.topontiki.gr/category/athlitika?page={}'.format(x) for x in range(0,TOPONTIKI_VARS['SPORT_PAGES'])]
    kathimerini_urls = ['https://www.kathimerini.gr/box-ajax?id=b1_1885015423_371795634&page={}'.format(x) for x in range(0,KATHIMERINI_VARS['SPORT_PAGES'])] 
    newpost_urls = ['http://newpost.gr/athlitika?page={}'.format(x) for x in range(1,NEWPOST_VARS['SPORT_PAGES'])]
    periodista_urls = ['http://www.periodista.gr/athlhtika-paraskhnia?start={}'.format(x) for x in range(0,PERIODISTA_VARS['SPORT_PAGES'],30)]
    tovima_urls = ['https://www.tovima.gr/category/sports/page/{}'.format(x) for x in range(1,TOVIMA_VARS['SPORT_PAGES'])]
    urls = url + kathimerini_urls + newpost_urls + periodista_urls + tovima_urls + topontiki_urls
    start_urls = urls[:]

    rules = (
        Rule(LinkExtractor(allow=('topontiki.gr/article/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_topontiki', follow=True), 
        Rule(LinkExtractor(allow=(r'popaganda\.gr.+newstrack/'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_popaganda', follow=True), 
        Rule(LinkExtractor(allow=(r'\.naftemporiki\.gr/story|\.naftemporiki\.gr/storypn'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_naftemporiki', follow=True), 
        Rule(LinkExtractor(allow=(r"\.kathimerini\.gr.+epikairothta/a8lhtismos/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_kathimerini', follow=True), 
        Rule(LinkExtractor(allow=(r"\.tovima\.gr.+sports"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tovima', follow=True), 
        Rule(LinkExtractor(allow=(r"\.tanea\.gr.+sports"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tanea', follow=True), 
        Rule(LinkExtractor(allow=('iefimerida.gr/spor'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_iefimerida', follow=True), 
        Rule(LinkExtractor(allow=('gazzetta.gr/football/','gazzetta.gr/basketball/','gazzetta.gr/other-sports/','gazzetta.gr/volleyball/','gazzetta.gr/tennis/'), 
        deny=('power-rankings','vid','gallery','pic')),callback='clear_gazzetta', follow=True),    
        Rule(LinkExtractor(allow=('sport24.gr/football/','sport24.gr/sports/','sport24.gr/Basket/'), 
        deny=('vid','gallery','pic')),callback='parse_sport24', follow=True),
        Rule(LinkExtractor(allow=('cnn.gr/news/sports')),callback='parse_cnn', follow=True),
        Rule(LinkExtractor(allow=('reader.gr/athlitismos'), deny=('vid')), callback='parse_reader_crawl', follow=True),
        Rule(LinkExtractor(allow=('thetoc.gr/athlitika'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_thetoc', follow=True),
        Rule(LinkExtractor(allow=('protagon.gr/epikairotita/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_protagon', follow=True),
        Rule(LinkExtractor(allow=(r"\.in\.gr.+/sports/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_in', follow=True), 
        Rule(LinkExtractor(allow=('newpost.gr/athlitika'), deny=()), callback='parse_newpost', follow=True),
        Rule(LinkExtractor(allow=('periodista.gr/athlhtika-paraskhnia'), deny=()), callback='parse_periodista', follow=True), 
        )

    
    #function for items from sport24
    def parse_sport24(self,response):
        #check if we are in an articles url
        title = response.xpath('//div[@class="storyContent"]/h1/text()').get()
        if title is not None:
            #get article's text
            text = response.xpath('//div[@itemprop="articleBody"]//p/text()|//div[@itemprop="articleBody"]//h3/text()|//div[@itemprop="articleBody"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)
            clear_escape = re.sub(r'\n|\t',"",clear_characters)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_escape)
            url = response.url
            subtopic = url.split('/')[3]
            if flag is None:
                yield {
                    "subtopic": subtopic,
                    "website" : SPORT24_VARS['WEBSITE'],
                    "title": title,
                    "date": response.xpath('//span[@class="byline_date"]/b/text()').get(),
                    "author": response.xpath('//span[@class="byline_author"]/b/text()').get(),
                    "text": clear_escape, 
                    "url": url
                }

    #function for items from gazzetta
    def clear_gazzetta(self, response):
        #check if we are in an articles url
        title = response.xpath('//div[@class="field-item even"]/h1/text()').get()
        if title is not None:
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
            else:
                author = response.xpath('//h3[@class="blogger-social"]/a/text()').get()
            yield {
                "subtopic": subtopic,
                "website": GAZZEETTA_VARS['WEBSITE'],
                "title": title,
                "date": response.xpath('//div[@class="article_date"]/text()').get(),
                "author": author,
                "text": response.xpath('//div[@itemprop="articleBody"]//p/text()|//p/a/text()|//p/strong/text()').getall() ,#|//div[@itemprop="articleBody"]//p/a/text()|div[@itemprop="articleBody"]//p/strong/text()').getall(),
                "url": url
            }

#function for cnn crawl
    def parse_cnn(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@class="story-title"]/text()').get() 
        if title is not None:
            #get article's text
            text = response.xpath('//p/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            url = response.url
            yield {
                "subtopic": GENERAL_CATEGORIES['SPORT'],
                "website": CNN_VARS['WEBSITE'],
                "title": title,
                "date": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get()),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-author"]/text()').get()),
                "text": re.sub( r'\n',"",clear_characters),
                "url": url,                
            }

    #the next two functions needed to crawl reader.gr
    def parse_reader_crawl(self,response):
        links = response.xpath('//h1[@class="article-title"]/a/@href|//div[@class="row region"]').getall()
        for link in links:
            if len(link) < READER_VARS['MAX_LINKS']:
                url = response.urljoin(link)
                yield Request(url,callback=self.parse_reader_item)


    def parse_reader_item(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1/text()').get() 
        if title is not None:
            #get article's text
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
            if title is not None:
                yield {
                    "subtopic": GENERAL_CATEGORIES['SPORT'],
                    "website": READER_VARS['AUTHOR'],
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
            if len(text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": GENERAL_CATEGORIES['SPORT'],
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
        if title is not None:
            sub = response.xpath('//span[@class="s_roumpr"]/a/text()').get()
            if sub == GENERAL_CATEGORIES['SPORT']:
                #get article's text
                text = response.xpath('//div[@class="left-single-column "]//p/text()|//div[@class="left-single-column "]//strong/text()|//div[@class="left-single-column "]//p/*/text()').getall()
                list_to_string = " ".join(" ".join(text))
                markspaces = re.sub( "  ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                final_text = re.sub( "space", " ",uneeded_spaces)
                clear_characters = re.sub( "\xa0","",final_text)

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)

                author = re.findall(r"(\w+).(\w+)",response.xpath('//strong[@class="generalbold uppercase"]/a/text()').get())
                list_to_tuple = author[0]
                author = ' '.join(list_to_tuple)

                date = re.findall(r"(\d+).(\w+).(\d+)",response.xpath('//span[@class="generalight uppercase"]/text()').get())
                list_to_tuple = date[0]
                date = ' '.join(list_to_tuple)

                url = response.url
                #check if we are in an article and that it doesn't have images
                if len(text)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    yield {
                        "subtopic": sub,
                        "website": re.search(r"www.+\.gr",url).group(0),
                        "title": title,
                        "date": date, 
                        "author": author,
                        "text": re.sub( r'\s\s\s',"",text),
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
                    "subtopic": GENERAL_CATEGORIES['SPORT'],
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
                    "subtopic": GENERAL_CATEGORIES['SPORT'],
                    "website": NEWPOST_VARS['WEBSITE'],
                    "title": title,
                    "date": (response.xpath('//small[@class="article-created-time"]/text()').get()).split('/')[0], 
                    "author": NEWPOST_VARS['WEBSITE'],
                    "text": re.sub( r'\s\s\s',"",clear_characters),
                    "url": url,                
            }

    def parse_periodista(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@itemprop="headline"]/text()').get() 
        if title is not None:
            #get article's text
            text = response.xpath('//div[@class="per-item-page-part per-article-body"]//p/text()|//div[@class="per-item-page-part per-article-body"]//strong/text()|//div[@class="per-item-page-part per-article-body"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)
            url = response.url

            #flag to see later on if we have videos
            flag = re.search(r"binteo|foto",url)

            #check if we are in an article, and if it doesn't have videos
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": GENERAL_CATEGORIES['SPORT'],
                    "website": re.search(r"www.+\.gr",url).group(0),
                    "title": re.sub( r'\t|\n|\r',"",title),
                    "date": re.sub(r'\t|\n|\r',"",response.xpath('//div[@class="col-md-4 per-color-grey per-font-size-md per-padding-top-20"]/text()').get()), 
                    "author": PERIODISTA_VARS['WEBSITE'],
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
            url = response.url

            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": GENERAL_CATEGORIES['SPORT'],
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

            #get subtopic from url
            url = response.url
            subtopic = url.split('/')[7]
            if len(subtopic)>TANEA_VARS['SUBTOPIC_LENGTH_ALLOWED'] :
                subtopic = GENERAL_CATEGORIES['SPORT']
            
            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": subtopic,
                    "website": TANEA_VARS['AUTHOR'],
                    "title": final_title,
                    "date": response.xpath('//span[@class="firamedium postdate updated"]/text()').get(), 
                    "author": TANEA_VARS['AUTHOR'],
                    "text": re.sub( r'\s\s\s|\n',"",clear_characters),
                    "url": url,                
                }

    def parse_tovima(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@class="entry-title thirty black-c zonabold"]/text()').get() 
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
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": GENERAL_CATEGORIES['SPORT'],
                    "website": TOVIMA_VARS['AUTHOR'],
                    "title": final_title,
                    "date": response.xpath('//time/span/text()').get(), 
                    "author": TOVIMA_VARS['AUTHOR'],
                    "text": re.sub( r'\s\s\s|\n',"",clear_characters),
                    "url": url,                
                }

    def parse_kathimerini(self,response):
        #check if we are in an articles url
        title = response.xpath('//h2[@class="item-title"]/text()').get() 
        if title is not None:
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

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            
            author = response.xpath('//span[@class="item-author"]/a/text()').get()
            if author == KATHIMERINI_VARS['CATEGORY_AUTHOR'] :
                author = KATHIMERINI_VARS['AUTHOR']

            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                yield {
                    "subtopic": GENERAL_CATEGORIES['SPORT'],
                    "website": KATHIMERINI_VARS['AUTHOR'],
                    "title": final_title,
                    "date": re.search(r"(\d+).(\w+).(\d+)",response.xpath('//time/text()').get()).group(0), 
                    "author": author,
                    "text": re.sub( r'\s\s\s|\n',"",clear_characters),
                    "url": url,                
                }

    def parse_naftemporiki(self,response):
        #check if we are in an articles url
        title = response.xpath('//h2[@id="sTitle"]/text()').get() 
        if title is not None:
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
                list_to_string = " ".join(" ".join(text))
                markspaces = re.sub( "  ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                final_text = re.sub( "space", " ",uneeded_spaces)
                clear_characters = re.sub("\xa0","",final_text)

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url
                
                #check if we are in an article and that it doesn't have images
                if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    yield {
                        "subtopic": response.xpath('//div[@class="Breadcrumb"]/a[2]/text()').get(),
                        "website": NAFTEMPORIKI_VARS['AUTHOR'],
                        "title": final_title,
                        "date": response.xpath('//div[@class="Date"]/text()').get(), 
                        "author": NAFTEMPORIKI_VARS['AUTHOR'],
                        "text": re.sub( r'\s\s\s|\n',"",clear_characters),
                        "url": url,                
                    }

    def parse_popaganda(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1/text()').get()
        if title is not None:
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
                list_to_string = " ".join(" ".join(text))
                markspaces = re.sub( "  ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                final_text = re.sub( "space", " ",uneeded_spaces)
                clear_characters = re.sub("\xa0","",final_text)

                author = response.xpath('//div[@class="author"]/a/text()|//div[@itemprop="author"]/*/text()').get()
                if author == None:
                    author = POPAGANDA_VARS['WEBSITE']

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url

                #check if we are in an article and that it doesn't have images
                if title is not None and len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    yield {
                        "subtopic": POPAGANDA_VARS['SPORT'],
                        "website": POPAGANDA_VARS['WEBSITE'],
                        "title": final_title,
                        "date": re.search(r'\d+\.\d+\.\d+',response.xpath('//div[@class="date"]/text()').get()).group(0), 
                        "author": POPAGANDA_VARS['WEBSITE'],
                        "text": re.sub( r'\s\s\s|\n',"",clear_characters),
                        "url": url,                
                    }

    def parse_topontiki(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1/text()').get()
        if title is not None:
            #check if we are in the correct category
            sub = response.xpath('//h2/a/text()').get()
            if sub == TOPONTIKI_VARS['CATEGORY_SPORT']:
                #fix title's format
                list_to_string = " ".join(" ".join(title))
                markspaces = re.sub( "       ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                put_spaces_back = re.sub( "space", " ",uneeded_spaces)
                final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

                #get article's text
                text = response.xpath('//div[@class="field-item even"]//p/text()|//div[@class="field-item even"]//p/*/text()|//div[@class="field-item even"]//p//span/text()').getall()
                list_to_string = " ".join(" ".join(text))
                markspaces = re.sub( "  ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                final_text = re.sub( "space", " ",uneeded_spaces)
                clear_characters = final_text.replace("\xa0","")

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url
                
                #check if we are in an article and that it doesn't have images
                if title is not None and len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH'] and flag is None:
                    yield {
                        "subtopic": GENERAL_CATEGORIES['SPORT'],
                        "website": TOPONTIKI_VARS['WEBSITE'],
                        "title": final_title,
                        "date": response.xpath('//span[@class="date"]/text()').get(), 
                        "author": TOPONTIKI_VARS['WEBSITE'],
                        "text": re.sub( r'\s\s\s|\n',"",clear_characters),
                        "url": url,                
                    }
