# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from app import db
from app.models import MenuEntry as DBMenuEntry
import datetime
from scrapy.exceptions import DropItem


class FilterDuplicates(object):
    def process_item(self, item, spider):

        db_matches = db.session.query(DBMenuEntry).filter_by(
            category=item['category'],
            mensa=item['mensa'],
            description=item['description'],
            date_valid=item['date_valid']
        ).all()

        if db_matches:
            # If there is more than one matching entry in the database, we probably
            # already saved a duplicate by accident.  I really hope that doesn't happen.
            assert(len(db_matches) == 1)

            spider.crawler.stats.inc_value('items_already_in_db')
            raise DropItem(
                "Menu item already found in database.\n"
                "Previously scraped on: {previous_scrape_time}".format(
                    previous_scrape_time=str(db_matches[0].time_scraped)))
        else:
            return item


class SaveToDatabase:
    def process_item(self, item, spider):
        new_entry = DBMenuEntry(
                    mensa=item['mensa'],
                    description=item['description'],
                    date_valid=item['date_valid'],
                    category=item['category'],
                    time_scraped=datetime.datetime.utcnow())
        db.session.add(new_entry)
        db.session.commit()
