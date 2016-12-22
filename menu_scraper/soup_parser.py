# This component is responsible for reading the HTML menu tables that are
# posted on the university's website and parsing them, using BeautifulSoup4,
# into my database format.
import re
import datetime
import menu_scraper.items


def get_all_menu_items(soup):
    """
    Find all the menus on the web page and break them down into database items.
    :param soup: A BeautifulSoup object made from an HTML mensa menu page
    :return: An iterator of MenuEntry objects for every menu entry on
    the web page.
    """
    for table in get_menu_tables(soup):
        for entry in parse_table(table):
            yield entry


# The details in the summary attribute always say "Ausgabe B (aktuelle
# Woche)", even if you're looking at Ausgabe A or nächste Woche.  It's dumb.
# TODO? change this so it just looks for a substring like 'Wochenplan Uweg'?
def get_menu_tables(soup):
    return soup.findAll('table', attrs={
        'summary': 'Wochenplan Uweg Ausgabe B (aktuelle Woche)'})


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
    assert(len(date_range) == 5)

    table_body = menu_table.find('tbody')
    # Each row in the table is a category in the menu.
    # Skip the first row.  It's just the days of the week.
    for row in table_body.find_all('tr')[1:]:
        tds = row.find_all('td')
        assert(len(tds) == 6)  # 1 for the category name + 5 days of the week

        category_name = re.sub('[^a-zA-Z]', '', tds[0].text)

        for td, date in zip(tds[1:], date_range):
            menu_items = td.find_all('div', attrs={'class': 'speise_eintrag'})
            for menu_item in menu_items:
                # Each item has its allergens listed after it in parentheses,
                # e.g. 'Spaghetti (Gl)'
                # We want to split this into its components:
                # ['Spaghetti', '(Gl)', '']
                item_split = re.split("(\(.+?\))", menu_item.text.strip())
                description = item_split[0].strip().replace("\n", " ")\
                                                   .replace('Ã¼', 'ü')\
                                                   .replace('Ã¶', 'ö')\
                                                   .replace('Ã¤', 'ä')\
                                                   .replace('ÃŸ', 'ß')
                # Some items do not have allergens.
                allergens = item_split[1] if len(item_split) == 3 else ""

                yield menu_scraper.items.MenuEntry(
                    # price=category_price,
                    mensa="Uhlhornsweg Ausgabe A",
                    category=category_name,
                    description=description,
                    date_valid=date,
                    allergens=allergens
                )


def get_date_range_from_string(date_range_string):
    """
    Parse the 5 day long date range that is usually posted above a menu.
    :param date_range_string: E.g. "(31.01.16 - 04.02.16)"
    :return A list of five datetime.date objects representing the dates the menu
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


def price_from_category(category_string):
    """Use a regex to grab the price out of a posted category.
    :param category_string: The contents of a 'category' box in a mensa menu
     table, e.g. "Pasta 1,30"
    :return A price in Euros, expressed as a float. e.g. 1.3
    """
    regex_string = "[0-9],[0-9][0-9]"
    matches = re.findall(regex_string, category_string)
    number_of_matches = len(matches)
    if number_of_matches == 1:
        price = float(matches[0].replace(',', '.'))
        return price
    elif number_of_matches == 0:
        raise PriceParsingError("A price could not be found for the given "
                                "category ('{1}').  The regex '{0}'"
                                " did not produce any matches."
                                .format(regex_string, category_string))
    elif number_of_matches > 1:
        raise PriceParsingError("A price could not be determined for the given "
                                "category ('{1}'). The regex '{0}' produced "
                                "more than one match: {2}"
                                .format(regex_string, category_string, matches))


class DateRangeParsingError(ValueError):
    """Indicates a problem parsing the date range posted above a menu."""


class PriceParsingError(ValueError):
    """Used to indicate that something went wrong while parsing the price of a
    menu item."""


class TableParsingError(ValueError):
    """Indicates something went wrong while parsing a menu table."""
