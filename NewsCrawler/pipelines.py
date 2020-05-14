# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from NewsCrawler.settings import DB_CREDS
import mysql.connector
class NewsCrawlerPipeline(object):

    def __init__(self):
        self.create_connection()

    def create_connection(self):
        self.conn = mysql.connector.connect(
            host = DB_CREDS['host'],
            user = DB_CREDS['user'],
            passwd = DB_CREDS['pass'],
            database = DB_CREDS['db']
        )
        self.curr = self.conn.cursor()

    def process_item(self, item, spider):
        self.store_db(item)
        return item
    
    def store_db(self,item):
        self.curr.execute("""insert into articles (subtopic, website, title, article_date, author, article_body, url) values (%s,%s,%s,%s,%s,%s,%s)""",(
            item['subtopic'],
            item['website'],
            item['title'],
            item['article_date'],
            item['author'],
            item['article_body'],
            item['url'],
        ))
        self.conn.commit()
