#!/usr/bin/env bash
set -euo pipefail

# Run database migrations if enabled (default: true)
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    echo "🔄 Running database migrations..."
    python manage.py migrate --noinput
fi

# Collect static files if enabled (default: true)
if [ "${COLLECT_STATIC:-true}" = "true" ]; then
    echo "📦 Collecting static files..."
    python manage.py collectstatic --noinput
fi

echo "🚀 Starting Gunicorn server on 0.0.0.0:${PORT:-8000}..."
exec gunicorn EduManage.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --access-logfile - \
    --error-logfile -
