#!/usr/bin/env bash
# dev.sh — Levanta TFinder en modo desarrollo con hot reload.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

VENV_UVICORN="$ROOT/venv/bin/uvicorn"

echo "=== Levantando infraestructura (postgres, redis, rabbitmq, mailhog) ==="
docker compose up -d postgres redis rabbitmq mailhog >/dev/null 2>&1 || true

echo "=== Esperando healthchecks ==="
sleep 4

echo "=== Levantando backends con --reload ==="
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

"$VENV_UVICORN" mesas_api.main:app --port 8001 --reload &
PID_MESAS=$!
"$VENV_UVICORN" builds_api.main:app --port 8002 --reload &
PID_BUILDS=$!
"$VENV_UVICORN" feed_api.main:app --port 8003 --reload &
PID_FEED=$!
"$VENV_UVICORN" notif_api.main:app --port 8004 --reload &
PID_NOTIF=$!

echo "=== Levantando frontend con Vite (HMR) ==="
cd frontend
npm run dev -- --port 5173 &
PID_FE=$!
cd "$ROOT"

echo ""
echo "TFinder dev levantado:"
echo "  Frontend (Vite HMR): http://localhost:5173"
echo "  Mesas API:           http://localhost:8001/docs"
echo "  Builds API:          http://localhost:8002/docs"
echo "  Feed API:            http://localhost:8003/docs"
echo "  Notif API:           http://localhost:8004/docs"
echo "  RabbitMQ UI:         http://localhost:15673"
echo "  MailHog UI:          http://localhost:8025"
echo ""
echo "PIDs: mesas=$PID_MESAS builds=$PID_BUILDS feed=$PID_FEED notif=$PID_NOTIF fe=$PID_FE"
echo "Para detener: kill $PID_MESAS $PID_BUILDS $PID_FEED $PID_NOTIF $PID_FE"

wait
