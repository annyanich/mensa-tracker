web: gunicorn flask_app:app
dbupgrade: python3 flask_manage.py db upgrade
scrapemenu: python3 menu_scraper/main.py
celeryworker: bin/run_celery_worker.sh
queuedailyemails: python3 queue_daily_emails.py