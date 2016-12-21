import scrapy

from bs4 import BeautifulSoup
from menu_scraper.soup_parser import get_all_menu_items


class MensaSpider(scrapy.Spider):
    name = "mensa_spider"
    allowed_domains = ["studentenwerk-oldenburg.de"]
    start_urls = [
        # "http://www.studentenwerk-oldenburg.de/gastronomie/speiseplaene"
        # "/uhlhornsweg-ausgabe-b.html",
        # "http://www.studentenwerk-oldenburg.de/gastronomie/speiseplaene"
        # "/uhlhornsweg-culinarium.html,"
        "http://www.studentenwerk-oldenburg.de/de/gastronomie/speiseplaene"
        "/uhlhornsweg-ausgabe-a.html"
    ]

    def parse(self, response):
        soup = BeautifulSoup(response.body.decode(response.encoding), "lxml")
        items = get_all_menu_items(soup)
        # Filter out empty items
        return [item for item in items if item['description']]
