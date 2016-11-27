from app.models import SavedSearch, MenuEntry

import datetime
import unicodedata

from itertools import groupby

EMAIL_BODY_TEMPLATE = """Hi, {name}!
You've signed up to receive email alerts when certain items appear in the mensa.
Tomorrow, the following items matching your search terms are on the menu:

{search_results}Guten Appetit!
Your Mensa tracker team (http://mensa-tracker.herokuapp.com)
"""

EMAIL_SUBJECT_TEMPLATE = "Mensa tracker alert for {date}"


def tomorrow():
    return datetime.date.today() + datetime.timedelta(days=1)


def menu_entries_tomorrow():
    return MenuEntry.query.filter_by(date_valid=tomorrow()).all()


def does_search_match(search_terms, body):
    def normalize_caseless(text):
        return unicodedata.normalize("NFKD", text.casefold())
    return normalize_caseless(search_terms) in normalize_caseless(body)


def run_all_searches_for_tomorrow():
    """
    Run all the Saved Searches in the database against the menu entries for tomorrow.
    :return: An iterator of pairs (SavedSearch, MenuEntry) with one pair for every time a search
    matches a menu entry.
    """
    for search in SavedSearch.query.all():
        for entry in menu_entries_tomorrow():
            if does_search_match(search.search_terms, entry.description):
                yield (search, entry)


def menu_entry_to_text(entry):
    return ("{date_valid}\n"
            "{mensa}: {category}\n"
            "{description}").format(
        description=entry.description.replace("\n", " "),
        mensa=entry.mensa,
        category=entry.category,
        date_valid=entry.date_valid.strftime("%A, %d.%m.%Y")
    )


def search_hits_to_emails(search_hits):
    """
    :param search_hits: A list of two-tuples of the form (SavedSearch, MenuEntry), whereby
    each menu entry is a hit for the corresponding search.
    :return: A list of three-tuples of the form (Email Recipient, Subject, Body), whereby
    each tuple represents one email to be sent out.
    """

    subject = EMAIL_SUBJECT_TEMPLATE.format(date=tomorrow().strftime("%A, %d.%m.%Y"))

    # Use groupby to group the search hits by the owner of the search.
    # This produces a list of tuples: (User, iterator((SavedSearch1, MenuEntry1), (search2, entry2), ...))
    for search_owner, hits_for_user in groupby(search_hits, lambda x: x[0].owner):
        formatted_search_results = ""

        # Group multiple hits for the same search together.
        for search, hits_for_search in groupby(hits_for_user, lambda x: x[0]):
            formatted_search_results += ('Search: "{0}"\n\n'.format(search.search_terms))

            # Put a blank line after each search result.
            for _, menu_entry in hits_for_search:
                formatted_search_results += menu_entry_to_text(menu_entry) + "\n\n"

        # Fill out the email body template with the information we have gathered
        body = EMAIL_BODY_TEMPLATE.format(name=search_owner.nickname,
                                          search_results=formatted_search_results)

        yield (search_owner.email, subject, body)


def test_email_generation():
    for recipient, subject, body in search_hits_to_emails(run_all_searches_for_tomorrow()):
        print("Recipient: {0}\n"
              "Subject: {1}\n"
              "Body: {2}\n".format(recipient, subject, body))

