# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from scrapy import Item
class NewsRecPipeline(object):
    def process_item(self, item, spider):
        # self.insert_db(item)
        self.insert_mysql(item)
        return item

    # 打开数据库
    def open_spider(self, spider):
        self.db = pymysql.connect('localhost','root',
                                  'root', 'rec',
                                  charset='utf8')
        # self.cursor = self.db.cursor(DictCursor)
        self.cursor = self.db.cursor()
        self.ori_table = 'news_table'

    # 关闭数据库
    def close_spider(self, spider):
        print("关闭"+ spider.name +"项目爬虫。。。")
        self.cursor.close()
        # self.db_conn.connection_pool.disconnect()
# 插入数据
    def insert_db(self, item):
        if isinstance(item, Item):
            item = dict(item)
    def insert_mysql(self,item):
        sql='''insert into {0} (pubtime,title,content,url) VALUES ('{1}','{2}','{3}','{4}') '''.format(self.ori_table,item.get('pubtime', ''),
            item.get('title',''),pymysql.escape_string(item.get('content','')),item.get('url',''))
        # print(sql)
        try:
            self.cursor.execute(sql)
            print('写入成功')
        except BaseException as e:
            # print(e)
            print("异常sql:"+sql)

