#!/usr/bin/env sh
set -e

# Run database migrations (skip gracefully if alembic dir is not ready)
if [ -f "alembic.ini" ] && [ -d "alembic/versions" ]; then
  echo "Running Alembic database migrations..."
  alembic upgrade head || echo "WARNING: Alembic migration failed, continuing with existing schema..."
fi

# Start the FastAPI application
echo "Starting TRUVEX Platform on port ${PORT:-8000}..."
exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
