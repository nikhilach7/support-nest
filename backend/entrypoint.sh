#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
python - <<'PY'
import socket
import time

host = "db"
port = 5432

while True:
    try:
        with socket.create_connection((host, port), timeout=1):
            break
    except OSError:
        time.sleep(0.1)

print("PostgreSQL is ready!")
PY

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000
