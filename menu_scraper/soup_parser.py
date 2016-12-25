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
    """
    The 'summary' attribute should be something like
    "Wochenplan Uweg Ausgabe B (aktuelle Woche)".
    """
    def is_menu_table(tag):
        return tag.name == 'table' and tag.has_attr('summary')\
            and 'Wochenplan' in tag['summary']

    return soup.findAll(is_menu_table)


def parse_table(menu_table):
    """
    Extract the name, price, allergens, etc. of every menu item in a table.
    :param menu_table: An HTML table object extracted by BeautifulSoup.
    :return A list of MenuEntry Items describing all the dishes on the menu.
    """
    # The date range of the table is posted above it.
    date_range = get_date_range_from_string(menu_table.previous_sibling)

    table_body = menu_table.find('tbody')

    # Skip the first row, because it's just the days of the week.
    for category_row in table_body.find_all('tr', recursive=False)[1:]:
        entries_monday_to_friday = get_menu_entries_for_five_days(category_row)

        for td, date in zip(entries_monday_to_friday, date_range):
            menu_item_elements = td.find_all(attrs={'class': 'speise_eintrag'})

            for element in menu_item_elements:
                item = item_from_string(element.text)
                item['category'] = get_category_name_from_row(category_row)
                item['date_valid'] = date
                if not item['price']:
                    item['price'] = get_price_from_row(category_row)
                yield item


def get_date_range_from_string(date_range_string):
    """
    Parse the date range that is usually posted above a menu.
    :param date_range_string: E.g. "(31.01.16 - 04.02.16)"
    :return A list of datetime.date objects representing the dates the menu
    is valid for.
    """
    date_regex = '[0-9][0-9]\.[0-9][0-9]\.[0-9][0-9]'
    date_strings = re.findall(date_regex, date_range_string)
    assert len(date_strings) == 2, (
        'The date range string found above a menu does not contain exactly '
        'two dates as determined by our Regex. \n'
        'Date string: {0}\nRegex: {1}'.format(date_range_string,
                                              date_regex))

    # Convert from strings into datetime.date values
    dates = [datetime.datetime.strptime(string, "%d.%m.%y").date()
             for string in date_strings]
    start_date, end_date = dates[0], dates[1]

    assert start_date < end_date, (
        'The start date posted above a menu came before the end date: ' +
        date_range_string)

    range_length = (end_date - start_date).days + 1

    assert range_length == 5, (
        "We assume that each menu covers five days, but this menu has the "
        "following dates posted above it: \n{0}\n "
        "Maybe our assumption is no longer true.".format(date_range_string))

    date_range = [(start_date + datetime.timedelta(days=n))
                  for n in range(range_length)]
    return date_range


def get_menu_entries_for_five_days(category_row):
    cells = category_row.find_all('td', recursive=False)
    assert len(cells) == 6, (
        "A row in the Speisekarte should be six columns wide: One category "
        "name plus five days' worth of menu entries. This row is either too "
        "wide or not wide enough: \n" +
        "\n".join("Column {i}: {text}".format(i=i, text=td.text)
                  for i, td in enumerate(cells)))

    return cells[1:]


def get_price_from_row(category_row):
    """
    :return: The price (in cents), if any, listed in the first cell of the row.
    If there is no price listed, return None.
    """
    first_cell_in_row = category_row.find('td', recursive=False)
    return get_price_from_string(first_cell_in_row.text)


def get_category_name_from_row(category_row):
    """
    Clean up e.g. "Haupt-\ngericht", "Beilagen\n 0,35", "Veggie/Vegan"
    to give us "Hauptgericht", "Beilagen", "Veggie/Vegan"
    """
    first_cell_in_row = category_row.find('td', recursive=False)
    return re.sub('[^a-zA-ZäüößÄÜÖ/]', '', first_cell_in_row.text)


def item_from_string(item_string):
    """
    Extract the price (if listed), name, and allergens of a menu item.
    :param item_string: Something like 'Spaghetti (Gl)' or 'Eisbergsalat 0,35'
    :return: A MenuEntry Item object usable by Scrapy
    """
    # Split the item_string into its components, e.g.
    # ['Spaghetti', '(Gl)', ''] or ['Eisbergsalat 0,35']
    item_split = re.split("(\(.+?\))", item_string.strip())
    assert len(item_split) == 1 or len(item_split) == 3

    allergens = item_split[1] if len(item_split) == 3 else ""

    price = get_price_from_string(item_string)

    item_name = fix_garbled_german_characters(item_split[0])
    item_name = strip_price_from_string(item_name)
    item_name = clean_up_whitespace(item_name)

    return menu_scraper.items.MenuEntry(
        price=price,
        description=item_name,
        allergens=allergens
    )


def fix_garbled_german_characters(string):
    """This is a workaround for a weird encoding issue I ran into."""
    return string.replace('Ã¼', 'ü')\
                 .replace('Ã¶', 'ö')\
                 .replace('Ã¤', 'ä')\
                 .replace('ÃŸ', 'ß')


def clean_up_whitespace(string):
    """
    Line-wrapped hyphenated words get put back together.
    Newlines become spaces.
    Double spaces become single spaces.
    Leading and trailing whitespace goes away.
    """
    string_without_line_wraps = re.sub("-\s*", "-", string)
    return ' '.join(string_without_line_wraps.split())


def strip_price_from_string(string):
    return re.sub("[0-9],[0-9][0-9]", "", string)


def get_price_from_string(string):
    match = re.search("([0-9],[0-9][0-9])", string)
    return int(match.group(0).replace(',', '')) if match else None
