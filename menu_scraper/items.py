# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MenuEntry(scrapy.Item):
    """
    Analogous to a row in the database table 'menu_entries'.
    TODO Resolve confusion between app.models.MenuEntry and this class.
    """
    date_valid = scrapy.Field()
    description = scrapy.Field()
    category = scrapy.Field()
    mensa = scrapy.Field()