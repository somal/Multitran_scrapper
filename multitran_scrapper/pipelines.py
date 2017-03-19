# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy import *
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .database import DATABASE

DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**DATABASE))


def create_translation_table(engine):
    DeclarativeBase.metadata.create_all(engine)


class Translation(DeclarativeBase):
    __tablename__ = "dictionaries"

    id = Column(Integer, primary_key=True)
    dictionary = Column('dictionary', String)
    word = Column('word', String)
    translation = Column('translation', String)
    author_name = Column('author_name', String, nullable=True)
    author_link = Column('author_link', String, nullable=True)


class MultitranScrapperPipeline(object):
    def __init__(self):
        engine = db_connect()
        create_translation_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
        translation = Translation(**item)

        try:
            session.add(translation)
            session.commit()
        except:
            session.rollback()
            print('rollback')
        finally:
            session.close()

        return item
