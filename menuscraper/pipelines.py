# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from app import db
from app.models import MenuEntry as DBMenuEntry
import datetime


class DatabasePipeline(object):
    def process_item(self, item, spider):
        db_entry = DBMenuEntry(mensa=item['mensa'],
                               description=item['description'],
                               date_valid=item['date_valid'],
                               category=item['category'],
                               time_scraped=datetime.datetime.utcnow())
        db.session.add(db_entry)
        db.session.commit()
        # TODO filter out duplicate menu entries
        # TODO Make time_scraped be the same for all items scraped in a run.

