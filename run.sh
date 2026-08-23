#!/bin/bash
set -e

echo "=== DEBUG: Checking environment variables ==="
echo "POSTGRES_HOST: $POSTGRES_HOST"
echo "POSTGRES_DATABASE_NAME: $POSTGRES_DATABASE_NAME"
echo "POSTGRES_USERNAME: $POSTGRES_USERNAME"
echo "POSTGRES_PORT: $POSTGRES_PORT"
echo "DATABASE_URL: $DATABASE_URL"
echo "=============================================="

echo "Applying migrations..."
alembic upgrade head

echo "Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000