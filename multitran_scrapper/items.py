# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TranslationItem(scrapy.Item):
    """
    This item is used in multitrtan_all_dictionaries for save translations. Example: http://www.multitran.com/m.exe?a=110&sc=801&l1=1&l2=2
    It hasn't some recommendation system and additional info, only full info from page
    """
    dictionary = scrapy.Field()
    word = scrapy.Field()
    translation = scrapy.Field()
    author_name = scrapy.Field()
    author_link = scrapy.Field()
