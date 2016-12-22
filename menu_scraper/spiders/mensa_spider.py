import scrapy
from config import menu_urls_and_names

from menu_scraper.soup_parser import get_all_menu_items


class MensaSpider(scrapy.Spider):
    name = "mensa_spider"
    allowed_domains = ["studentenwerk-oldenburg.de"]

    start_urls = list(menu_urls_and_names.keys())

    def parse(self, response):
        items = get_all_menu_items(response)
        # Filter out empty items
        return [item for item in items if item['description']]
