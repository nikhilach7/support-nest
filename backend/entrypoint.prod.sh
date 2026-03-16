#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
python - <<'PY'
import socket, time, os

host = os.environ.get("DB_HOST", "localhost")
port = int(os.environ.get("DB_PORT", 5432))

while True:
    try:
        with socket.create_connection((host, port), timeout=1):
            break
    except OSError:
        time.sleep(0.5)

print("PostgreSQL is ready!")
PY

echo "Running migrations..."
python manage.py migrate --no-input

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
