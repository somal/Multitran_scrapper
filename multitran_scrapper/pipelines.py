# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy import *
from sqlalchemy.engine.url import URL

from .database import DATABASE


class MultitranScrapperPipeline(object):
    def __init__(self):
        self.engine = create_engine(URL(**DATABASE))

    def process_item(self, item, spider):
        return item
