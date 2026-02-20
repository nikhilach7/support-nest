FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . /app/

# Create entrypoint script (no extra OS packages required)
RUN cat <<'EOF' > /app/entrypoint.sh
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
EOF

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
