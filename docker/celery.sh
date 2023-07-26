#!/bin/bash

sleep 5
echo "Run Celery"
poetry run celery -A app.tasks.email_sender:celery_mail worker --loglevel=INFO 