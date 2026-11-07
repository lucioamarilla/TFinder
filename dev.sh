#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

VENV_UVICORN="$ROOT/venv/bin/uvicorn"

echo "=== Levantando infraestructura (postgres, redis, rabbitmq) ==="
docker compose up -d postgres redis rabbitmq >/dev/null 2>&1 || true

echo "=== Esperando healthchecks ==="
sleep 4

echo "=== Levantando backend con --reload ==="
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

"$VENV_UVICORN" mesas_api.main:app --port 8001 --reload &
PID_MESAS=$!

echo "=== Levantando frontend con Vite (HMR) ==="
cd frontend
npm run dev -- --port 5173 &
PID_FE=$!
cd "$ROOT"

echo ""
echo "TFinder dev levantado:"
echo "  Frontend (Vite HMR): http://localhost:5173"
echo "  Mesas API:           http://localhost:8001/docs"
echo "  RabbitMQ UI:         http://localhost:15673"
echo ""
echo "PIDs: mesas=$PID_MESAS fe=$PID_FE"
echo "Para detener: kill $PID_MESAS $PID_FE"

wait