# This component is responsible for reading the HTML menu tables that are
# posted on the university's website and parsing them, using BeautifulSoup4,
# into my database format.
import re
import datetime
import menu_scraper.items
from config import menu_urls_and_names
from bs4 import BeautifulSoup


def get_all_menu_items(response):
    """
    Find all the menus on the web page and break them down into database items.
    :param response: A Response object from Scrapy.
    :return: An iterator of MenuEntry objects for every menu entry on
    the web page.
    """
    soup = BeautifulSoup(response.body.decode(response.encoding), "lxml")
    for table in get_menu_tables(soup):
        for entry in parse_table(table):
            entry['mensa'] = menu_urls_and_names[response.url]
            yield entry


def get_menu_tables(soup):
    # The summary attribute for the table with the menu plan says something
    # like "Wochenplan Uweg Ausgabe B (aktuelle Woche)".
    def is_menu_table(tag):
        return tag.name == 'table' and tag.has_attr('summary')\
            and 'Wochenplan' in tag['summary']
    return soup.findAll(is_menu_table)


def parse_table(menu_table):
    """
    Parse an HTML table used to display a mensa's weekly menu.
    Transform each entry on the menu into a MenuEntry describing the
    dish's name, allergens, category, and when and where it is being offered.

    :param menu_table: An HTML table object extracted by BeautifulSoup.
    :return A list of MenuEntry Items describing all the dishes offered in
    the menu.
    """
    # The date range of the table is posted above it.
    date_range = get_date_range_from_string(menu_table.previous_sibling)
    assert len(date_range) == 5, ("We assume that each menu covers five days, "
                                  "but this menu has the following date range "
                                  "posted above it:\n{0}\n"
                                  "Maybe this assumption is no longer "
                                  "true.".format(
                                   "\n".join(str(date) for date in date_range)))

    table_body = menu_table.find('tbody')
    # Each row in the table is a category in the menu.
    # Skip the first row.  It's just the days of the week.
    for row in table_body.find_all('tr', recursive=False)[1:]:
        tds = row.find_all('td', recursive=False)
        assert len(tds) == 6, ("A row in the Speisekarte should be six "
                               "columns wide: One category name plus five "
                               "days' worth of menu entries. This row is "
                               "either too wide or not wide enough: \n") + \
            "\n".join("Column {i}: {text}".format(i=i, text=td.text) for i, td in enumerate(tds))

        # Contents e.g. "Haupt-\ngericht", "Beilagen\n 0,35", "Veggie/Vegan"
        category_name = re.sub('[^a-zA-ZäüößÄÜÖ\/]', '', tds[0].text)

        # Sometimes a price is posted next to the category name.
        category_price_match = re.search("[0-9],[0-9][0-9]", tds[0].text)

        # Iterate through five cells of the menu, corresponding to five days
        # of the week
        for td, date in zip(tds[1:], date_range):
            menu_item_divs = td.find_all(attrs={'class': 'speise_eintrag'})
            for menu_item_div in menu_item_divs:

                # Each item has its allergens listed after it in parentheses,
                # e.g. 'Spaghetti (Gl)', 'Eisbergsalat 0,35'
                # We want to split these into their components:
                # item_split=['Spaghetti', '(Gl)', ''] or ['Eisbergsalat 0,35']
                item_split = re.split("(\(.+?\))", menu_item_div.text.strip())
                assert len(item_split) == 1 or len(item_split) == 3

                # Extract allergens.  See comment above
                allergens = item_split[1] if len(item_split) == 3 else ""

                # Extract the item's name.  First, fix garbled German letters
                item_name = item_split[0].replace('Ã¼', 'ü')\
                                         .replace('Ã¶', 'ö')\
                                         .replace('Ã¤', 'ä')\
                                         .replace('ÃŸ', 'ß')

                # Remove the price, if present, from the item's name
                item_name = re.sub("[0-9],[0-9][0-9]", "", item_name)

                # Remove the extra space that is present when a word is
                # hyphenated and split across two lines
                item_name = re.sub("-\s*", "-", item_name)

                # Finally, clean up whitespace.
                # Newlines become spaces.  Trailing whitespace goes away.
                # Double spaces become single spaces.
                item_name = ' '.join(item_name.split())

                # Get the item's price. If there's no price next to the
                # category, there's usually one posted next to the item itself.
                if category_price_match:
                    price_string = category_price_match.group(0)
                else:
                    item_price_match = re.search("[0-9],[0-9][0-9]", menu_item_div.text)
                    if category_name != 'Pastasauce' and item_name != 'Salatbar':
                        assert item_price_match, \
                               ("We expect to see a price listed for every "
                                "item, except for Pastasauce and Salatbar.  "
                                "This item does not have a price: \n"
                                "Name: {name}\nCategory: {cat}\nDate: {date}".format(
                                   name=item_name, cat=category_name, date=date
                                ))
                    price_string = item_price_match.group(0) \
                        if item_price_match else '0'

                yield menu_scraper.items.MenuEntry(
                    price=int(price_string.replace(',', '')),
                    category=category_name,
                    description=item_name,
                    date_valid=date,
                    allergens=allergens
                )


def get_date_range_from_string(date_range_string):
    """
    Parse the date range that is usually posted above a menu.
    :param date_range_string: E.g. "(31.01.16 - 04.02.16)"
    :return A list of datetime.date objects representing the dates the menu
    is valid for.
    """

    # The dates are formatted "(dd.mm.yy - dd.mm.yy)".
    # Use a regex to match them.
    regex = re.compile('[0-9][0-9]\.[0-9][0-9]\.[0-9][0-9]')
    date_strings = regex.findall(date_range_string)
    if len(date_strings) != 2:
        raise DateRangeParsingError(
                'The date range found for a menu (\'{0}\') does not '
                'contain exactly two dates matched by the regex: {1}'.format(
                    date_range_string,
                    regex.pattern))

    # Convert from strings into datetime.date values
    dates = [datetime.datetime.strptime(string, "%d.%m.%y").date()
             for string in date_strings]
    start_date, end_date = dates[0], dates[1]

    if start_date > end_date:
        raise DateRangeParsingError('The start date came before the end date: '
                                    '{0}'.format(date_range_string))

    range_length = (end_date - start_date).days + 1
    date_range = [(start_date + datetime.timedelta(days=n))
                  for n in range(range_length)]
    return date_range


class DateRangeParsingError(ValueError):
    """Indicates a problem parsing the date range posted above a menu."""
