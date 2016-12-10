from flask_app.models import SavedSearch, MenuEntry, User

import datetime
import unicodedata

EMAIL_BODY_TEMPLATE = """Hi, {name}!
You've signed up to receive email alerts when certain items appear in the mensa.
Today, the following items matching your search terms are on the menu:

{search_results}Guten Appetit!
Ann Yanich (http://mensa-tracker.herokuapp.com)
"""

EMAIL_SUBJECT_TEMPLATE = "Mensa tracker alert for {date}"


def menu_entries_today():
    return MenuEntry.query.filter_by(date_valid=datetime.date.today()).all()


def does_search_match(search_terms, body):
    def normalize_caseless(text):
        return unicodedata.normalize("NFKD", text.casefold())
    return normalize_caseless(search_terms) in normalize_caseless(body)


def menu_entry_to_text(entry):
    return ("{date_valid}\n"
            "{mensa}: {category}\n"
            "{description}").format(
        description=entry.description.replace("\n", " "),
        mensa=entry.mensa,
        category=entry.category,
        date_valid=entry.date_valid.strftime("%A, %d.%m.%Y")
    )


def email_alerts_for_today():
    """
    For each user, run their saved searches.  Write an email to them if they have
    search results.

    :return: A list of three-tuples of the form (Email Recipient, Subject, Body), whereby
    each tuple represents one email to be sent out.
    """

    email_subject = EMAIL_SUBJECT_TEMPLATE.format(date=datetime.date.today().strftime("%A, %d.%m.%Y"))

    for user in User.query.all():
        formatted_search_results = ""

        for search in SavedSearch.query.filter_by(owner=user).all():
            search_results = [menu_entry for menu_entry in menu_entries_today()
                              if does_search_match(search.search_terms, menu_entry.description)]

            if search_results:
                formatted_search_results += ('Search: "{0}"\n\n'.format(search.search_terms))
                for menu_entry in search_results:
                    formatted_search_results += menu_entry_to_text(menu_entry) + "\n\n"

        if formatted_search_results == "":
            continue;  # Do not send an email if there are no search results.

        # Fill out the email body template with the information we have gathered
        email_body = EMAIL_BODY_TEMPLATE.format(name=user.nickname,
                                                search_results=formatted_search_results)

        yield (user.email, email_subject, email_body)


def test_email_generation():
    for recipient, subject, body in email_alerts_for_today():
        print("Recipient: {0}\n"
              "Subject: {1}\n"
              "Body: {2}\n".format(recipient, subject, body))

