from locale import currency

from flask_app.models import SavedSearch, MenuEntry, User

import datetime
import unicodedata

EMAIL_BODY_TEMPLATE = """Hi, {name}!
You've signed up to receive email alerts when certain items appear in the Mensa.
Today, the following items matching your search terms are on the menu:

{search_results}Guten Appetit!
Ann Yanich (http://mensa-tracker.herokuapp.com)
"""

EMAIL_SUBJECT_TEMPLATE = "Mensa tracker alert for {date}"


def test_email_generation(date):
    # TODO convert this into a unit test
    for recipient, subject, body in email_alerts_for_date(date):
        print("Recipient: {0}\n"
              "Subject: {1}\n"
              "Body: {2}\n".format(recipient, subject, body))


def email_alerts_for_today():
    return email_alerts_for_date(datetime.date.today())


def email_alerts_for_date(date):
    """
    For each user, run their saved searches.  Write an email to them if they have
    search results.

    :return: A list of three-tuples of the form (Email Recipient, Subject, Body), whereby
    each tuple represents one email to be sent out.
    """

    email_subject = EMAIL_SUBJECT_TEMPLATE.format(date=date.strftime("%A, %d.%m.%Y"))

    for user in User.query.all():
        formatted_search_results = ""

        for search in SavedSearch.query.filter_by(owner=user).all():
            search_results = [menu_entry for menu_entry in menu_entries_for_date(date)
                              if does_search_match(search.search_terms, menu_entry.description)]

            if search_results:
                formatted_search_results += ('Search: "{0}"\n\n'.format(search.search_terms))
                for menu_entry in search_results:
                    formatted_search_results += menu_entry_to_text(menu_entry) + "\n\n"

        if formatted_search_results == "":
            continue  # Do not send an email if there are no search results.

        # Fill out the email body template with the information we have gathered
        email_body = EMAIL_BODY_TEMPLATE.format(name=user.nickname,
                                                search_results=formatted_search_results)

        yield (user.email, email_subject, email_body)


def menu_entries_for_date(date):
    return MenuEntry.query.filter_by(date_valid=date).all()


def does_search_match(search_terms, body):
    def normalize_caseless(text):
        return unicodedata.normalize("NFKD", text.casefold())
    return normalize_caseless(search_terms) in normalize_caseless(body)


def menu_entry_to_text(entry):
    return ("{date_valid}\n"
            "{mensa}\n"
            "{category}\n"
            "{description}\n"
            "{price}").format(
        description=entry.description.replace("\n", " "),
        mensa=entry.mensa,
        category=entry.category,
        date_valid=entry.date_valid.strftime("%A, %d.%m.%Y"),
        price=currency(entry.price/100)
    )


if __name__ == "__main__":
    test_email_generation(datetime.date(2017, 1, 12))
