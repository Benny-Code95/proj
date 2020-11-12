# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst


class SpiderTstItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class NewsItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class NewsItem(scrapy.Item):
    title = scrapy.Field()
    date = scrapy.Field()
    detail = scrapy.Field()