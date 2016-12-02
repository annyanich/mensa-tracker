# This is a script which is intended to be run once a day.
# It runs all of the searches in the database against the menu for tomorrow,
# then it queues up an email to each user who has at least one search result.

from email_alerter.email_alerter import email_alerts_for_today
from email_alerter import celery_tasks

if __name__ == '__main__':
    for recipient, subject, body in email_alerts_for_today():
        celery_tasks.send_email.delay(recipient, subject, body)
        # TODO log the emails we send out?
