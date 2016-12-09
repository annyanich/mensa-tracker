web: gunicorn app:app
dbupgrade: python3 run.py db upgrade
scrapemenu: python3 menuscraper/main.py
celeryworkerdebug: celery worker --app=email_alerter.celery_tasks.app -l DEBUG
celeryworker: celery worker --app=email_alerter.celery_tasks.app
queuedailyemails: python3 queue_daily_emails.py