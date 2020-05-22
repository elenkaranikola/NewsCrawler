# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    topic = scrapy.Field
    subtopic = scrapy.Field()
    website = scrapy.Field()
    title = scrapy.Field()
    article_date = scrapy.Field()
    author = scrapy.Field()
    article_body =  scrapy.Field()
    url = scrapy.Field()
    pass
