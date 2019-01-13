import celery
import logging
import yagmail
import config
from smtplib import SMTPAuthenticationError

# To run a worker, run this command in a linux shell (in the root directory
# of the project):
# celery worker --app=email_alerter.celery_tasks.app -l DEBUG
#
# To add a message to the queue, open a iPython shell
# and do this:
#
# import celery_tasks
# tasks.send_email.delay(recipients='',subject='',body='')
#
# If a worker is running and connected to the message queue, it should pick
# up the task
# and execute it, displaying the result somewhere in its debug output.

app = celery.Celery('celery_tasks')
app.conf.update(BROKER_URL=config.CLOUDAMQP_URL, BROKER_POOL_LIMIT=1)


@app.task()
def send_email(recipients, subject, body):
    logging.info("Queuing email with recipients: {}, subject: {}".format(
        recipients, subject))
    try:
        yag = yagmail.SMTP(config.GMAIL_USERNAME, config.GMAIL_PASSWORD)
        result = yag.send(to=recipients, subject=subject, contents=body)
    except SMTPAuthenticationError as e:
        logging.error("Sending an email to {} failed: {}".format(recipients, e))
        raise

    return result
