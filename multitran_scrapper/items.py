# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TranslationItem(scrapy.Item):
    dictionary = scrapy.Field()
    word = scrapy.Field()
    translation = scrapy.Field()
    author_name = scrapy.Field()
    author_link = scrapy.Field()
