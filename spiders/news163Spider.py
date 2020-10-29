# -*- coding: utf-8 -*-
import json
from bs4 import BeautifulSoup, Comment
from scrapy import Spider, Request
from scrapy.settings.default_settings import DEFAULT_REQUEST_HEADERS
import re
from news_rec.items import NewsRecItem

class News163Spider(Spider):
    name = 'news_163_spider'
    allowed_domains = ['163.com']
    start_urls = "http://news.163.com/special/0001220O/news_json.js"
    def start_requests(self):
        DEFAULT_REQUEST_HEADERS['Accept'] = '*/*'
        DEFAULT_REQUEST_HEADERS['Host'] = 'news.163.com'
        DEFAULT_REQUEST_HEADERS['Referer'] = 'http://news.163.com/'
        req = Request(self.start_urls.format(category="news"),callback=self.parse_list,meta={"title":"ContentList"}, encoding='utf-8')
        yield req

    def parse_list(self, response):
        #163爬取的response数据是gzip解压过来的 这里没办法自动转码 要随时调整
        try:
            j_str=response.body.decode("gb18030")
        except UnicodeDecodeError as e:
            j_str = response.body.decode("utf-8")
            print("163.com下gb18030解码失败,已转utf-8")
        else:
            # json_str = re.search(r"data=((.|\s)*?);", j_str).group(1)
            json_str = j_str[9:-1]
            list_json = json.loads(json_str)
            # content_list=list_json['result']['data']
            for i in range(0, 1):
                for con in list_json["news"][i]:
                    msg = response.meta
                    msg["url"] = con["l"]
                    msg["title"] = con["t"]
                    msg["pubtime"] = con["p"]
                    yield Request(msg["url"], callback=self.parse_content, meta=msg)
    def parse_content(self, response):
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            if "news.163.com" in response.request.url:
                source_content = soup.find("div", id="endText")
                news_source = soup.find("a", id="ne_article_source").get_text()
                # 清除延伸阅读
                if source_content.find("div", class_="related_article related_special") is not None:
                    source_content.find("div", class_="related_article related_special").extract()
                if source_content.find("p", class_="otitle") is not None:
                    source_content.find("p", class_="otitle").extract()
                content = source_content
                urlset_tmp = self.crawler.stats.get_value("urlset")
                item = NewsRecItem()
                item['title'] = response.meta.get("title", "")
                item['pubtime'] = response.meta.get("pubtime", "")
                item["content"] = content.prettify()
                item["url"] = response.request.url
                yield item
            else:
                print("163域名下爬取网站列表不匹配")
                return ''
        except BaseException as e:
            print("提取内容失败：" + response.request.url)
            return
