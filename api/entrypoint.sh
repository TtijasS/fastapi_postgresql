#!/usr/bin/env sh
set -e

# Make 'import app.*' work no matter where we run from
export PYTHONPATH=/app

# Run DB migrations (generate init migration automatically if none exist)
cd /app
echo "Running Alembic migrations..."
if [ ! -d "/app/alembic/versions" ] || [ -z "$(ls -A /app/alembic/versions 2>/dev/null)" ]; then
  echo "No migrations found; creating initial autogenerate migration..."
  alembic revision --autogenerate -m "init"
fi
alembic upgrade head

echo "Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers
