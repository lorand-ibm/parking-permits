#!/bin/bash

set -e

if [[ "$DEV_SERVER" = "true" ]]; then
    python /app/manage.py runserver 0.0.0.0:8000
else
    echo 'TODO in the next PR: gunicorn application server command here'
fi
