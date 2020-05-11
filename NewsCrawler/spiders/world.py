# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from NewsCrawler.items import NewsCrawlerItem
from NewsCrawler.settings import PERIODISTA_VARS,PRESSPROJECT_VARS,IEFIMERIDA_VARS,TANEA_VARS,TOVIMA_VARS
from NewsCrawler.settings import KATHIMERINI_VARS,NAFTEMPORIKI_VARS,LIFO_VARS,EFSYN_VARS
from NewsCrawler.settings import POPAGANDA_VARS,TOPONTIKI_VARS,GENERAL_CATEGORIES

class DogSpider(CrawlSpider):
    name = 'world'
    allowed_domains = [
        'topontiki.gr',
        'popaganda.gr',
        'efsyn.gr',
        'lifo.gr',
        'naftemporiki.gr',
        'kathimerini.gr',
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
        'https://popaganda.gr/newstrack/world/',
        'https://www.naftemporiki.gr/world',
        'https://www.tanea.gr',
        'https://www.cnn.gr/',
        'https://www.reader.gr/news/diethni',
        'https://www.thetoc.gr/',
        'https://www.protagon.gr/epikairotita/',
        'http://www.periodista.gr/',
        'https://www.in.gr/world/',
        'https://www.thepressproject.gr/',
        'https://www.iefimerida.gr',
        ]
    topontiki_urls = ['http://www.topontiki.gr/category/kosmos?page={}'.format(x) for x in range(0,TOPONTIKI_VARS['WORLD_PAGES'])]
    efsyn_urls = ['https://www.efsyn.gr/kosmos?page={}'.format(x) for x in range(1,EFSYN_VARS['WORLD_PAGES'])]
    lifo_urls = ['https://www.lifo.gr/now/world/page:{}'.format(x) for x in range(1,LIFO_VARS['WORLD_PAGES'])]
    kathimerini_urls = ['https://www.kathimerini.gr/box-ajax?id=b1_1885015423_1231434187&page={}'.format(x) for x in range(0,KATHIMERINI_VARS['WORLD_PAGES'])]
    newpost_urls = ['http://newpost.gr/kosmos?page={}'.format(x) for x in range(1,18713)]
    periodista_urls = ['http://www.periodista.gr/kosmos?start={}'.format(x) for x in range(1,PERIODISTA_VARS['WORLD_PAGES'],10)]
    tovima_urls = ['https://www.tovima.gr/category/world/page/{}'.format(x) for x in range(1,TOVIMA_VARS['WORLD_PAGES'])]
    urls = url + kathimerini_urls + newpost_urls + periodista_urls + tovima_urls + lifo_urls + efsyn_urls
    start_urls = urls[:]


    rules = (
        Rule(LinkExtractor(allow=('topontiki.gr/article/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_topontiki', follow=True), 
        Rule(LinkExtractor(allow=(r'popaganda\.gr.+newstrack/'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_popaganda', follow=True), 
        Rule(LinkExtractor(allow=(r'www\.efsyn\.gr'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_efsyn', follow=True), 
        Rule(LinkExtractor(allow=(r'www\.lifo\.gr.+world/'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_lifo', follow=True), 
        Rule(LinkExtractor(allow=(r'\.naftemporiki\.gr/story|\.naftemporiki\.gr/storypn'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_naftemporiki', follow=True), 
        Rule(LinkExtractor(allow=(r"\.kathimerini\.gr.+epikairothta/kosmos/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_kathimerini', follow=True), 
        Rule(LinkExtractor(allow=(r"\.tovima\.gr.+world"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tovima', follow=True), 
        Rule(LinkExtractor(allow=(r"\.tanea\.gr.+world"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tanea', follow=True), 
        Rule(LinkExtractor(allow=('iefimerida.gr/kosmos'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_iefimerida', follow=True), 
        Rule(LinkExtractor(allow=('thepressproject'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_thepressproject', follow=True), 
        Rule(LinkExtractor(allow=('periodista.gr/kosmos'), deny=()), callback='parse_periodista', follow=True), 
        Rule(LinkExtractor(allow=('cnn.gr/news/kosmos'), deny=('cnn.gr/news/kosmos/gallery/','protoselida')), callback='parseItemCnn', follow=True),
        Rule(LinkExtractor(allow=('reader.gr/news/diethni'), deny=('vid')), callback='parseItemReader', follow=True),
        Rule(LinkExtractor(allow=('thetoc.gr/diethni'), deny=('binteo','videos','gallery','eikones','twit')), callback='parseItemThetoc', follow=True), 
        Rule(LinkExtractor(allow=('protagon.gr/epikairotita/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parseItemProtagon', follow=True),
        Rule(LinkExtractor(allow=(r".in\.gr.+/world/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parseItemIn', follow=True), 
        Rule(LinkExtractor(allow=('newpost.gr/kosmos'), deny=()), callback='parseNewpost', follow=True), 
        )
#function to crawl cnn.gr    
    def parseItemCnn(self,response):
        title = response.xpath('//h1[@class="story-title"]/text()').get() 
        text = response.xpath('//div[@class="story-content"]//p/text()|//div[@class="story-content"]//strong/text()|//div[@class="story-content"]//a/text()').getall()
        listtostring = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",listtostring)
        uneededspaces = re.sub( " ", "",markspaces)
        finaltext = re.sub( "space", " ",uneededspaces)
        clearcharacters = re.sub( "\xa0","",finaltext)
        url = response.url
        if title is not None and len(clearcharacters)>10:
            yield {
                "subtopic": "World",
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": title,
                "date": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get()),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-author"]/text()').get()),
                "text": re.sub( r'\n|\t',"",clearcharacters),
                "url": url,                
            }
#function to crawl reader.gr 
    def parseItemReader(self,response):
        title = response.xpath('//h1/text()').get() 
        text = response.xpath('//div[@class="article-summary"]//p/text()|//div[@class="article-body"]//p/text()|//div[@class="article-body"]//p/*/text()').getall()
        listtostring = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",listtostring)
        uneededspaces = re.sub( " ", "",markspaces)
        finaltext = re.sub( "space", " ",uneededspaces)
        clearcharacters = re.sub( "\xa0","",finaltext)
        author = response.xpath('//p[@class="article-author"]/a/text()').get()
        if author is not None:
            author = re.sub("\xa0","",author)
        else:
            author = "Reader"
        url = response.url
        if title is not None:
            yield {
                "subtopic": "World",
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": re.sub( r'\n|\t',"",title),
                "date": re.sub( r'\n|\t',"",response.xpath('//time/text()').get()),
                "author": author,
                "text": re.sub( r'\n|\t',"",clearcharacters),
                "url": url,              
            }
    def parseItemThetoc(self,response):
        title = response.xpath('//div[@class="article-title"]//h1/text()').get() 
        text = response.xpath('//div[@class="article-content articleText"]//p/text()|//div[@class="article-content articleText"]//strong/text()|//div[@class="article-content articleText"]//p/*/text()').getall()
        listtostring = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",listtostring)
        uneededspaces = re.sub( " ", "",markspaces)
        finaltext = re.sub( "space", " ",uneededspaces)
        clearcharacters = re.sub( "\xa0","",finaltext)
        url = response.url
        if title is not None and len(clearcharacters)>10:
            yield {
                "subtopic": "World",
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": title,
                "date": " ".join(re.findall(r"[0-9]+.[α-ωΑ-Ω]+\..[0-9]+",response.xpath('//span[@class="article-date"]/text()').get())),
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="author-social"]//h5/a/span[2]/text()').get()),
                "text": re.sub( r'\n|\t',"",clearcharacters),
                "url": url,                
            }
            
    def parseItemProtagon(self,response):
        sub = response.xpath('//span[@class="s_roumpr"]/a/text()').get()
        if sub == "Κόσμος":
            title = response.xpath('//h1[@class="entry-title"]/text()').get() 
            text = response.xpath('//div[@class="left-single-column "]//p/text()|//div[@class="left-single-column "]//strong/text()|//div[@class="left-single-column "]//p/*/text()').getall()
            listtostring = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",listtostring)
            uneededspaces = re.sub( " ", "",markspaces)
            finaltext = re.sub( "space", " ",uneededspaces)
            clearcharacters = re.sub( "\xa0","",finaltext)
            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clearcharacters)
            url = response.url
            author = re.findall(r"(\w+).(\w+)",response.xpath('//strong[@class="generalbold uppercase"]/a/text()').get())
            #from list to tuple to string
            listtotuple = author[0]
            author = ' '.join(listtotuple)
            date = re.findall(r"(\d+).(\w+).(\d+)",response.xpath('//span[@class="generalight uppercase"]/text()').get())
            listtotuple = date[0]
            date = ' '.join(listtotuple)
            #check if we are in an article, and if it doesn't have images
            if title is not None and len(clearcharacters)>10 and flag is None:
                yield {
                    "subtopic": "World",
                    "website": re.search(r"www.+\.gr",url).group(0),
                    "title": title,
                    "date": date, 
                    "author": author,
                    "text": re.sub( r'\s\s\s',"",clearcharacters),
                    "url": url,                
                }
    def parse_periodista(self,response):
        title = response.xpath('//h1[@itemprop="headline"]/text()').get() 
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
        if title is not None and len(clear_characters)>10 and flag is None:
            yield {
                "subtopic": "World",
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": re.sub( r'\t|\n|\r',"",title),
                "date": re.sub(r'\t|\n|\r',"",response.xpath('//div[@class="col-md-4 per-color-grey per-font-size-md per-padding-top-20"]/text()').get()), 
                "author": "periodista.gr",
                "text": re.sub( r'\s\s\s',"",clear_characters),
                "url": url,                
            }   

    def parseItemIn(self,response):
        title = response.xpath('//h1[@class="entry-title black-c"]/text()').get() 
        text = response.xpath('//div[@class="main-content pos-rel article-wrapper"]//p/text()|//div[@class="main-content pos-rel article-wrapper"]//strong/text()|//div[@class="main-content pos-rel article-wrapper"]//p/*/text()').getall()
        listtostring = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",listtostring)
        uneededspaces = re.sub( " ", "",markspaces)
        finaltext = re.sub( "space", " ",uneededspaces)
        clearcharacters = re.sub( "\xa0","",finaltext)
        #flag to see later on if we have tweets ect
        flag = re.search(r"@",clearcharacters)
        url = response.url
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(clearcharacters)>10 and flag is None:
            yield {
                "subtopic": "World",
                "website": re.search(r"www.+\.gr",url).group(0),
                "title": title,
                "date": response.xpath('//time/text()').get(), 
                "author": response.xpath('//span[@class="vcard author"]//a/text()').get(),
                "text": re.sub( r'\s\s\s',"",clearcharacters),
                "url": url,                
            }

    def parseNewpost(self,response):
        title = response.xpath('//h1[@class="article-title"]/text()').get() 
        text = response.xpath('//div[@class="article-main clearfix"]//p/text()|//div[@class="article-main clearfix"]//strong/text()|//div[@class="article-main clearfix"]//p/*/text()').getall()
        listtostring = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",listtostring)
        uneededspaces = re.sub( " ", "",markspaces)
        finaltext = re.sub( "space", " ",uneededspaces)
        clearcharacters = re.sub( "\xa0","",finaltext)
        #flag to see later on if we have tweets ect
        flag = re.search(r"@",clearcharacters)
        url = response.url
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(clearcharacters)>10 and flag is None:
            yield {
                "subtopic": "World",
                "website": "newpost.gr",
                "title": title,
                "date": (response.xpath('//small[@class="article-created-time"]/text()').get()).split('/')[0], 
                "author": "Newpost.gr",
                "text": re.sub( r'\s\s\s',"",clearcharacters),
                "url": url,                
           }

    def parse_thepressproject(self,response):
        sub = response.xpath('//div[@class="article-categories"]/a/text()').get()
        if sub == "Διεθνή":
            title = response.xpath('//h1[@class="entry-title"]/text()|//h1[@class="entry-title"]/*/text()').get()
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

                #check if we are in an article, and if it doesn't have images
                if title is not None and len(clear_characters)>10 and flag is None:
                    yield {
                        "subtopic": "World",
                        "website": PRESSPROJECT_VARS['AUTHOR'],
                        "title": final_title,
                        "date": date, 
                        "author": PRESSPROJECT_VARS['AUTHOR'],
                        "text": re.sub( r'\s\s\s',"",clear_characters),
                        "url": url,                
                    }

    def parse_iefimerida(self,response):
        title = response.xpath('//h1/span/text()').get() 
        text = response.xpath('//div[@class="field--name-body on-container"]//p/text()|//div[@class="field--name-body on-container"]/strong/text()|//div[@class="field--name-body on-container"]//p/*/text()|//div[@class="field--name-body on-container"]//p//li/text()').getall()
        list_to_string = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        final_text = re.sub( "space", " ",uneeded_spaces)
        clear_characters = re.sub("\xa0","",final_text)

        #flag to see later on if we have tweets ect
        flag = re.search(r"@",clear_characters)
        url = response.url
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(final_text)>10 and flag is None:
            yield {
                "subtopic": "World",
                "website": IEFIMERIDA_VARS['AUTHOR'],
                "title": title,
                "date": re.sub(r"\|"," ",re.search(r"(\d+)\|(\d+)\|(\d+)",response.xpath('//span[@class="created"]/text()').get()).group(0)), 
                "author": IEFIMERIDA_VARS['AUTHOR'],
                "text": re.sub( r'\s\s\s|\n',"",final_text),
                "url": url,                
            }

    def parse_tanea(self,response):

        title = response.xpath('//h1[@class="entry-title black-c"]/text()').get() 
        #title = " ".join(" ".join(title))
        list_to_string = " ".join(" ".join(title))
        markspaces = re.sub( "       ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        put_spaces_back = re.sub( "space", " ",uneeded_spaces)
        final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)
        #final_title = re.sub(r'/s/s/s',)

        text = response.xpath('//div[@class="main-content pos-rel article-wrapper"]//p/text()|//div[@class="main-content pos-rel article-wrapper"]//strong/text()|//div[@class="main-content pos-rel article-wrapper"]//h3/text()|//div[@class="main-content pos-rel article-wrapper"]//p/*/text()').getall()
        list_to_string = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        final_text = re.sub( "space", " ",uneeded_spaces)
        clear_characters = re.sub("\xa0","",final_text)

        #flag to see later on if we have tweets ect
        flag = re.search(r"@",clear_characters)
        url = response.url
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(final_text)>10 and flag is None:
            yield {
                "subtopic": "World",
                "website": TANEA_VARS['AUTHOR'],
                "title": final_title,
                "date": response.xpath('//span[@class="firamedium postdate updated"]/text()').get(), 
                "author": TANEA_VARS['AUTHOR'],
                "text": re.sub( r'\s\s\s|\n',"",final_text),
                "url": url,                
            }

    def parse_tovima(self,response):
        title = response.xpath('//h1[@class="entry-title thirty black-c zonabold"]/text()').get() 
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
        
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(final_text)>10 and flag is None:
            yield {
                "subtopic": 'World',
                "website": TOVIMA_VARS['AUTHOR'],
                "title": final_title,
                "date": response.xpath('//time/span/text()').get(), 
                "author": TOVIMA_VARS['AUTHOR'],
                "text": re.sub( r'\s\s\s|\n',"",final_text),
                "url": url,                
            }

    def parse_kathimerini(self,response):
        title = response.xpath('//h2[@class="item-title"]/text()').get() 
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

        #flag to see later on if we have tweets ect
        flag = re.search(r"@",clear_characters)
        url = response.url
        
        author = response.xpath('//span[@class="item-author"]/a/text()').get()
        if author == "Κύριο Αρθρο" :
            author = KATHIMERINI_VARS['AUTHOR']

        #check if we are in an article, and if it doesn't have images
        if title is not None and len(final_text)>10 and flag is None:
            yield {
                "subtopic": 'World',
                "website": KATHIMERINI_VARS['AUTHOR'],
                "title": final_title,
                "date": re.search(r"(\d+).(\w+).(\d+)",response.xpath('//time/text()').get()).group(0), 
                "author": author,
                "text": re.sub( r'\s\s\s|\n',"",final_text),
                "url": url,                
            }

    def parse_naftemporiki(self,response):
        subtopic = response.xpath('//span[@itemprop="articleSection"]/text()').get()
        if subtopic == "ΚΟΣΜΟΣ" :
            title = response.xpath('//h2[@id="sTitle"]/text()').get() 
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
            
            #check if we are in an article, and if it doesn't have images
            if title is not None and len(final_text)>10 and flag is None:
                yield {
                    "subtopic": 'Greece',
                    "website": NAFTEMPORIKI_VARS['AUTHOR'],
                    "title": final_title,
                    "date": response.xpath('//div[@class="Date"]/text()').get(), 
                    "author": NAFTEMPORIKI_VARS['AUTHOR'],
                    "text": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                }

    def parse_lifo(self,response):
        title = response.xpath('//h1[@itemprop="headline"]/text()|//meta[@itemprop="headline"]/text()|//h1/*/text()').get() 
        list_to_string = " ".join(" ".join(title))
        markspaces = re.sub( "       ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        put_spaces_back = re.sub( "space", " ",uneeded_spaces)
        final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

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
        
        #check if we are in an article, and if it doesn't have images
        if title is not None and len(clear_characters)>10 and flag is None:
            yield {
                "subtopic": "World",
                "website": LIFO_VARS['AUTHOR'],
                "title": final_title,
                "date": response.xpath('//time/text()').get(), 
                "author": author,
                "text": re.sub( r'\s\s\s|\n',"",clear_characters),
                "url": url,                
            }

    def parse_efsyn(self,response):
        subtopic = response.xpath('//article/a/@href').get()
        category = subtopic.split('/')[1]
        if category == "kosmos":
            title = response.xpath('//h1[1]/text()').get() 
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
            

            #check if we are in an article, and if it doesn't have images
            if title is not None and len(clear_characters)>10 and flag is None:
                yield {
                    "subtopic": EFSYN_VARS['WORLD'],
                    "website": EFSYN_VARS['WEBSITE'],
                    "title": final_title,
                    "date": response.xpath('//time/text()').get(), 
                    "author": author,
                    "text": re.sub( r'\s\s\s|\n',"",clear_characters),
                    "url": url,                
                }

    def parse_popaganda(self,response):
        category = response.xpath('//div[@class="category"]/a/text()').get()

        if category == POPAGANDA_VARS['CATEGORY_WORLD'] :
            title = response.xpath('//h1/text()').get() 
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

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            #check if we are in an article, and if it doesn't have images
            if title is not None and len(clear_characters)>10 and flag is None:
                yield {
                    "subtopic": POPAGANDA_VARS['WORLD'],
                    "website": POPAGANDA_VARS['WEBSITE'],
                    "title": final_title,
                    "date": re.search(r'\d+\.\d+\.\d+',response.xpath('//div[@class="date"]/text()').get()).group(0), 
                    "author": POPAGANDA_VARS['WEBSITE'],
                    "text": re.sub( r'\s\s\s|\n',"",clear_characters),
                    "url": url,                
                }

    def parse_topontiki(self,response):
        sub = response.xpath('//h2/a/text()').get()
        if sub == TOPONTIKI_VARS['CATEGORY_WORLD']:
            title = response.xpath('//h1/text()').get() 
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
            
            #check if we are in an article, and if it doesn't have images
            if title is not None and len(clear_characters)>10 and flag is None:
                yield {
                    "subtopic": GENERAL_CATEGORIES['WORLD'],
                    "website": TOPONTIKI_VARS['WEBSITE'],
                    "title": final_title,
                    "date": response.xpath('//span[@class="date"]/text()').get(), 
                    "author": TOPONTIKI_VARS['WEBSITE'],
                    "text": re.sub( r'\s\s\s|\n',"",clear_characters),
                    "url": url,                
                }