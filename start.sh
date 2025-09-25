#!/usr/bin/env bash
set -e
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec gunicorn -b 0.0.0.0:$PORT camp_project.wsgi:application
