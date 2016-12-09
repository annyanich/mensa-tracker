#!/usr/bin/env sh
export PYTHONPATH=".."

if [ "$DEBUG" = "True" ]; then
    celery worker --app=email_alerter.celery_tasks.app -l DEBUG
else
    celery worker --app=email_alerter.celery_tasks.app
fi
