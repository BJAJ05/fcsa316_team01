#!/bin/sh
# Container start-up. With RUN_MIGRATIONS=1 the database schema is updated first
# (Docker Compose sets it; in Kubernetes a separate Job runs the migrations instead).
set -e

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
    python manage.py migrate --noinput
fi

# Replace this shell with the main process (gunicorn), so it receives stop signals directly.
exec "$@"
