# -*- coding: utf-8 -*-

# Scrapy settings for NewsCrawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'NewsCrawler'

SPIDER_MODULES = ['NewsCrawler.spiders']
NEWSPIDER_MODULE = 'NewsCrawler.spiders'

#DEPTH_LIMIT = 3
DOMAIN_DEPTHS = {'naftemporiki.gr': 0,'pontiki.gr': 1, 'efsyn.gr': 1, 'tovima.gr':1, 'newpost.gr':1, 'periodista.gr':1, 'lifo.gr': 1, 'kathimerini.gr':1, 'tanea.gr':1, 'popaganda':3}
# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 5

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 3
#CONCURRENT_REQUESTS_PER_IP = 1

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'NewsCrawler.middlewares.NewsCrawlerSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'NewsCrawler.middlewares.NewsCrawlerDownloaderMiddleware': 543,
#}
SPIDER_MIDDLEWARES = {
    'NewsCrawler.middlewares.DomainDepthMiddleware': 900,
    'scrapy.contrib.spidermiddleware.depth.DepthMiddleware': None
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
   'scrapy.extensions.telnet.TelnetConsole': None,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html 
ITEM_PIPELINES = {
    'NewsCrawler.pipelines.NewsCrawlerPipeline': 300,
}

DB_CREDS = {
    'host':'localhost',
    'user':'root',
    'pass':'eleni123',
    'db':'NewsCrawler'
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 10
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
#HTTPERROR_ALLOW_ALL = True


#APPLICATION SETTINGS
#-------------------------------------------------------------------------------------
#        MAX NUMBER OF PAGES IS 200
#-------------------------------------------------------------------------------------

PERIODISTA_VARS = {
   'WEBSITE': "peridista.gr",
	'ECONOMY_PAGES':10,
	'GREECE_PAGES':10,
	'POLITICS_PAGES':10,
   'WORLD_PAGES':10,
   'SPORT_PAGES':10,
}

SPORT24_VARS = {
   'WEBSITE': "sport24.gr"
}

GAZZEETTA_VARS = {
   'WEBSITE': "gazzetta.gr"
}

PRESSPROJECT_VARS = {
   'CATEGORY_WORLD': "Διεθνή",
   'CATEGORY_POLITICS': "Πολιτική",
   'CATEGORY_GREECE': "Ελλάδα",
   'CATEGORY_CULTURE': "Πολιτισμός",
   'CATEGORY_ECONOMICS': "Οικονομία",
   'AUTHOR': "thepressproject.gr"
}

IEFIMERIDA_VARS = {
   'AUTHOR': "iefimerida.gr"
}

TANEA_VARS = {
   'AUTHOR': "tanea.gr",
   'SUBTOPIC_LENGTH_ALLOWED': 15,
   'CINEMA_PAGES':2,
   'MUSIC_PAGES':3,
   'CULTURE_PAGES': 5,
   'FOOD_PAGES': 5,
   'WOMEN_PAGES': 3,
   'SCIENCE_PAGES': 8,
   'CATEGORY_CULTURE': "culture",
   'CATEGORY_STYLE': "Woman",
}

TOVIMA_VARS = {
   'AUTHOR': "tovima.gr",
   'POLITICS_PAGES': 15,
   'WORLD_PAGES': 15,
   'GREECE_PAGES': 15,
   'SCIENCE_PAGES': 15,
   'ECONOMICS_PAGES': 15,
   'SPORT_PAGES': 15,
   'CULTURE_PAGES': 15,
   'FOOD_PAGES': 15,
   'CATEGORY_TECH': "Science"
}

KATHIMERINI_VARS = {
   'AUTHOR': "kathimerini.gr",
   'GREECE_PAGES': 27,
   'WORLD_PAGES': 38,
   'ENVIRONMENT_PAGES': 20,
   'TECH_PAGES': 10,
   'SCIENCE_PAGES': 30,
   'SPORT_PAGES': 38,
   'POLITICS_PAGES': 33,
   'FOOD_PAGES': 30,
   'CULTURE_PAGES': 30,
   'ECONOMY_PAGES': 50,
   'CATEGORY_AUTHOR': "Κύριο Αρθρο",
   'CATEGORY_TECH': "Science",
}

NAFTEMPORIKI_VARS = {
   'AUTHOR': "naftemporiki.gr",
   'CATEGORY_POLITICS': "ΠΟΛΙΤΙΚΗ" ,
   'CATEGORY_ENVIRONMENT': "ΠΕΡΙΒΑΛΛΟΝ",
   'CATEGORY_GREECE': "ΚΟΙΝΩΝΙΑ",
   'CATEGORY_CULTURE': "ΠΟΛΙΤΙΣΤΙΚΑ",
   'CATEGORY_SPORT': "ΑΘΛΗΤΙΚΑ",
   'CATEGORY_WORLD': "ΚΟΣΜΟΣ",
}

LIFO_VARS = {
   'AUTHOR': "lifo.gr",
   'ENVIRONMENT_PAGES': 14,
   'POLITICS_PAGES': 14,
   'CULTURE_PAGES': 14,
   'WORLD_PAGES': 14,
   'TECH_PAGES': 14,
   'PEOPLE_PAGES': 14,
   'CATEGORY_TECH': "Tech & Science",
}

INSOMNIA_VARS = {
   'WEBSITE': "insomnia.gr"
}

EFSYN_VARS = {
   'WEBSITE': "efsyn.gr",
   'CATEGORY_WORLD': "kosmos",
   'CATEGORY_POLITICS': "politiki",
   'CATEGORY_GREECE': "ellada",
   'CATEGORY_CULTURE': "tehnes",
   'CATEGORY_ECONOMICS': "oikonomia",
   'POLITICS': "Politics",
   'ECONOMICS': "Economics",
   'GREECE': "Greece",
   'WORLD': "World",
   'ART': "Culture",
   'POLITICS_PAGES': 20,
   'ECONOMICS_PAGES': 20,
   'GREECE_PAGES': 20,
   'WORLD_PAGES': 20,
   'ART_PAGES': 25,
}

POPAGANDA_VARS = {
   'WEBSITE': "popaganda.gr",
   'GREECE': "Greece",
   'WORLD': "World",
   'CULTURE': "Culture",
   'ENVIRONMENT': "Environment",
   'SPORT': "Sport",
   'TECH': "Tech",
   'FOOD': "Food",
   'CATEGORY_GREECE': "ΕΛΛΑΔΑ",
   'CATEGORY_WORLD': "ΚΟΣΜΟΣ",
   'CATEGORY_CULTURE': "ΠΟΛΙΤΙΣΜΟΣ",
   'CATEGORY_ENVIRONMENT': "ΕΠΙΣΤΗΜΗ & ΠΕΡΙΒΑΛΛΟΝ",
   'CATEGORY_SPORT': "ΑΘΛΗΤΙΣΜΟΣ",
   'CATEGORY_TECH': "TECHNEWS",
}

TOPONTIKI_VARS = {
   'POLITICS_PAGES': 15,
   'ECONOMICS_PAGES': 15,
   'ENVIRONMENT_PAGES': 15,
   'SPORT_PAGES': 15,
   'WORLD_PAGES': 15,
   'CULTURE_PAGES': 15,
   'WEBSITE': "topontiki.gr",
   'CATEGORY_ECONOMICS': "ΟΙΚΟΝΟΜΙΑ",
   'CATEGORY_ENVIRONMENT': "ΠΕΡΙΒAΛΛΟΝ",
   'CATEGORY_GREECE': "ΕΛΛAΔΑ",
   'CATEGORY_POLITICS': "ΠΟΛΙΤΙΚΗ",
   'CATEGORY_SPORT': "ΑΘΛΗΤΙΚA",
   'CATEGORY_WORLD': "ΚΟΣΜΟΣ",
   'CATEGORY_CULTURE':'"Π" ART',
}

GENERAL_CATEGORIES = {
   'ALLOWED_LENGTH': 10,
   'ECONOMICS': "Economics",
   'POLITICS': "Politics",
   'GREECE': "Society",
   'WORLD': "World",
   'CULTURE': "Culture",
   'ENVIRONMENT': "Environment",
   'SPORT': "Sport",
   'TECH': "Tech",
   'FOOD': "Food",
   'STYLE': "Style",
}

READER_VARS = {
   'WEBSITE': "reader.gr",
   'AUTHOR': "reader.gr",
   'MAX_LINKS': 100,
}

PROTAGON_VARS = {
   'WEBSITE': "protagon.gr",
   'CATEGORY_TECH': "Επιστήμη & Τεχνολογία",
   'CATEGORY_POLITICS': "Πολιτική",
   'CATEGORY_ENVIRONMENT': "Περιβάλλον",
   'CATEGORY_ECONOMICS': "Οικονομία",
   'CATEGORY_GREECE': "Greece",
   'CATEGORY_CULTURE': "Πολιτισμός",
   'CATEGORY_WORLD': "Κόσμος",
}

NEWPOST_VARS = {
   'WORLD_PAGES': 33,
   'STYLE_PAGES': 33,
   'SPORT_PAGES': 33,
   'ECONOMICS_PAGES': 33,
   'CULTURE_PAGES': 33,
   'FOOD_PAGES': 33,
   'GREECE_PAGES': 33,
   'WEBSITE': "newpost.gr",
   'STYLE_SUBTOPIC': "Lifestyle",
}

CNN_VARS = {
   'ARTICLE_TYPE': "story",
   'CNN_CULTURE_PAGES': 20,
   'CNN_STYLE_PAGES': 20,
   'WEBSITE': "cnn.gr",
}

IN_VARS = {
   'WEBSITE': "in.gr",
   'STYLE_SUBTOPIC': "Health & Life",
   'CULTURE_SUBTOPIC': "Culture & Entertainment",
}

THETOC_VARS = {
   'WEBSITE': 'thetoc.gr',
   'full_date': "20"
}
NEWSIT_VARS = {
   'WEBSITE': 'newsit.gr'
}
