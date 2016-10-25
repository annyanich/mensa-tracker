import celery
import yagmail
import config

# To run a worker, run this command in a linux shell:
# celery worker --app=celery_tasks.app -l DEBUG
#
# To add a message to the queue, open a iPython shell
# and do this:
#
# import celery_tasks
# tasks.send_email.delay(recipients='',subject='',body='')
#
# If a worker is running and connected to the message queue, it should pick up the task
# and execute it, displaying the result somewhere in its debug output.

app = celery.Celery('celery_tasks')
# RabbitMQ config is currently stored in vagrant-init.sh.
app.conf.update(BROKER_URL='amqp://devuser:test123@localhost:5672/devvhost')


@app.task(bind=True)
def send_email(self, recipients, subject, body):
    # TODO Handle errors.  The task in Celery should "fail" if the email doesn't go out.
    yag = yagmail.SMTP(config.GMAIL_USERNAME, config.GMAIL_PASSWORD)
    result = yag.send(to=recipients, subject=subject, contents=body)
    return result

# Limit emails to 10/minute. This helps avoid instantly using up the entire Gmail limit
# of 500/day, should a glitch arise that queues up hundreds of emails at once.
app.control.rate_limit('celery_tasks.send_email', '10/m')