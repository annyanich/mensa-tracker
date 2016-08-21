# This component is responsible for reading the HTML menu tables that are
# posted on the university's website and parsing them, using BeautifulSoup4,
# into my database format.
import re
import datetime
import menuscraper.items


# The details in the summary attribute always say "Ausgabe B (aktuelle
# Woche)", even if you're looking at Ausgabe A or nächste Woche.  It's dumb.
# TODO? change this so it just looks for a substring like 'Wochenplan Uweg'?
def get_menu_tables(soup):
    return soup.findAll('table', attrs={
        'summary': 'Wochenplan Uweg Ausgabe B (aktuelle Woche)'})


class DateRangeParsingError(ValueError):
    """Indicates a problem parsing the date range posted above a menu."""


def get_date_range_from_string(date_range_string):
    """Parse the 5 day long date range that is usually posted above a menu.
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


class PriceParsingError(ValueError):
    """Used to indicate that something went wrong while parsing the price of a
    menu item."""


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


class TableParsingError(ValueError):
    """Indicates something went wrong with the parsing of a menu table."""


def parse_table(menu_table):
    """
    Parse an HTML table used to display a mensa's weekly menu.
    Transform each entry on the menu into a MenuEntry describing the
    dish's name, category, price, and when and where it is being offered.

    Currently, this function lumps together all the items in each category.
    For example, there is only one "Pasta" MenuEntry per day, and it
    represents all of the pastas and sauces on offer for that day.
    :param menu_table: An HTML table object extracted by BeautifulSoup.
    :return A list of MenuEntry Items describing all the dishes offered in
    the menu.
    """
    # Convert the table into a 2D array.
    # The first entry of each row will be a category of dish.  E.g. Alternativ,
    # Suppe, Dessert, Salat, or Pasta. The following five entries will contain
    # the names of the dishes offered on the five days of the week.
    data = []
    table_body = menu_table.find('tbody')
    rows = table_body.find_all('tr', recursive=False)
    for row in rows:
        cols = row.find_all('td', recursive=False)
        cols = [ele.text.strip() for ele in cols]
        data.append(cols)

    # The dates for which the menu is valid are posted right above it.
    date_range = get_date_range_from_string(menu_table.previous_sibling)

    # The menu is usually five days long. To be safe, let's make sure of that.
    date_range_length = len(date_range)
    if date_range_length != 5:
        raise TableParsingError("Date range above table is not exactly five "
                                "days long.  It's {0} days long."
                                .format(date_range_length))

    # Skip the first row of data, because it's just the days of the week.
    for row in data[1:]:

        # Each row is expected to have six items in the following order :
        # [Category name & price] [monday] [tuesday] [wednesday] [thursday] [friday]
        if len(row) is not 6:
            raise TableParsingError("A row of the menu is not exactly six items long."
                                    "Row: {row}"
                                    "(Expected format: [Category] [Monday] ... [Friday])"
                                    .format(row=row))

        category_string = row[0]
        category_name = re.sub('[^a-zA-Z]', '', category_string)
        category_price = price_from_category(category_string)

        for entry, date in zip(row[1:], date_range):
            entry = entry.replace('Ã¼', 'ü')\
                .replace('Ã¶', 'ö')\
                .replace('Ã¤', 'ä')\
                .replace('ÃŸ', 'ß')  # TODO Can this be fixed a nicer way?
            yield menuscraper.items.MenuEntry(
                # price=category_price,
                mensa="Uhlhornsweg Ausgabe A",
                category=category_name,
                description=entry,
                date_valid=date)


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
