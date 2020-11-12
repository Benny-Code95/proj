# coding: utf-8

import scrapy
# from MySpider.spider_tst.spider_tst.items import NewsItem, NewsItemLoader
import os


class NewSpider(scrapy.Spider):
    name = 'news'
    allowed_domains = 'http://www.haiwainet.cn/'
    start_urls = ['http://japan.haiwainet.cn/chinese/']

    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield scrapy.Request(url, self.parse)

    def parse(self, response):
        print(response.text())
        yield response.text()


if __name__ == '__main__':
    os.system('scrapy crawl news')
