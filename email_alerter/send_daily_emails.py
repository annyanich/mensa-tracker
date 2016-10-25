import celery_tasks
import datetime
import unicodedata

from app.models import SavedSearch, MenuEntry, User

# This is a script which is intended to be run once a day.  It runs all of the searches
# saved by every user in the database against the menu for tomorrow and queues up emails
# (using celery_tasks.send_email) to the users whose saved searches have hits, letting
# them know what items of interest will be on the menu tomorrow.


def tomorrow():
    return datetime.date.today() + datetime.timedelta(days=1)


def menu_entries_tomorrow():
    return MenuEntry.query.filter_by(date_valid=tomorrow()).all()


def search_query(saved_search, menu_entry):
    def normalize_caseless(text):
        return unicodedata.normalize("NFKD", text.casefold())
    return normalize_caseless(saved_search.search_terms) in normalize_caseless(menu_entry.description)


def queue_email(user_id, menu_entry):
    celery_tasks.send_email.delay(
        subject="Mensa menu alert for {0}".format(tomorrow()),
        body="""{0}""".format(menu_entry),
        recipients=User.query.filter_by(id=user_id).first().email
    )


def run_all_queries():
    for search in SavedSearch.query.all():
        for entry in menu_entries_tomorrow():
            if search_query(search, entry):
                queue_email(search.user_id, entry)

if __name__ == '__main__':
    run_all_queries()
