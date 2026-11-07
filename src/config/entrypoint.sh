#!/bin/bash

APP_PORT=${PORT:-8000}

cd /app/
exec /opt/venv/bin/gunicorn cfehome.wsgi:application --bind "0.0.0.0:${APP_PORT}"
