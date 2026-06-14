#!/bin/sh

set -eu

runtime_dir="${RUNTIME_DIR:-/tmp/ymmo-ia}"
health_url="${BACKEND_HEALTH_URL:-http://127.0.0.1:5000/healthz}"
port="${PORT:-5100}"
workers="${GUNICORN_WORKERS:-1}"
threads="${GUNICORN_THREADS:-4}"
timeout="${GUNICORN_TIMEOUT:-180}"

rm -rf "$runtime_dir"
mkdir -p "$runtime_dir"
cp -R /app/. "$runtime_dir/"
cd "$runtime_dir"

for i in $(seq 1 90); do
  if curl -fsS "$health_url" >/dev/null 2>&1; then
    break
  fi

  echo "Waiting for backend health at $health_url ($i/90)"
  sleep 2
done

exec gunicorn \
  --bind "0.0.0.0:${port}" \
  --workers "$workers" \
  --threads "$threads" \
  --timeout "$timeout" \
  --worker-tmp-dir /tmp \
  --access-logfile - \
  --error-logfile - \
  main:app
