#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h pg_db -p 5432 -U user; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up - running migrations"
cd /app
alembic upgrade head

echo "Starting application"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

