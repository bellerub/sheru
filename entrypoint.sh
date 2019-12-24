#!/bin/bash

# Wait for DB to come online
if [ -z "$DB_OVERRIDE" ]; then
    while !</dev/tcp/db/5432; do sleep 1; done;
fi

if [ -z "$WORKER" ]; then
    python manage.py makemigrations --noinput
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput 1> /dev/null
    daphne project.asgi:application -b 0.0.0.0 -p ${PORT:-8000} --proxy-headers
else
    python manage.py runworker
fi