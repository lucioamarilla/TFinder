#!/usr/bin/env bash
# Reinicia el stack con datos limpios. Es el unico script que borra estado.
#
# Uso:  bash scripts/demo/00-reset.sh
#
# El -v del down es imprescindible: sin el quedan mesas llenas, notificaciones
# acumuladas de corridas anteriores y usuarios de prueba. La slide 9 necesita
# que la mesa 2 tenga UNA sola vacante.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

banner "00 - RESET CON DATOS LIMPIOS"

docker compose down -v || fallo "docker compose down"
docker compose up -d --build || fallo "docker compose up"

banner "Esperando a que los cuatro servicios Respondan"
for puerto in 8001 8002 8003 8004; do
  if esperar_ready "http://127.0.0.1:$puerto/ready" 120; then
    ok "$puerto listo"
  else
    fallo "$puerto no respondio en 120 s"
  fi
done

esperado "los cuatro 200 con \"estado\":\"listo\""
resumen
echo
echo "  Siguiente:  bash scripts/demo/01-preparacion.sh"
