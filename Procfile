web: gunicorn app:app
init: python3 run.py db init
upgrade: python3 run.py db upgrade
scrapemenu: python3 menuscraper/main.py
celeryworkerdebug: celery worker --app=email_alerter.celery_tasks.app -l DEBUG
celeryworker: celery worker --app=email_alerter.celery_tasks.app
senddailyemails: python3 send_daily_emails.py