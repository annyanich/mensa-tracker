#!/usr/bin/env bash
celery worker --app=celery_tasks.app -l DEBUG