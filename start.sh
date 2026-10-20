#!/usr/bin/env bash
# Inicialização em produção (Render): migrações, dados de demonstração e servidor gunicorn.
set -euo pipefail
cd "$(dirname "$0")/src"
flask --app wsgi.py db upgrade
if [ -n "${SEED_PASSWORD:-}" ]; then
  flask --app wsgi.py seed
fi
exec gunicorn wsgi:app --bind "0.0.0.0:${PORT:-8000}" --workers 2 --timeout 60 --access-logfile -
