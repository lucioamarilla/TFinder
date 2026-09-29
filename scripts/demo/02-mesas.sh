#!/usr/bin/env bash
# Estado de las mesas, miembros, ids de cuentas, topologia de la mensajeria y
# checklist antes de hablar.
#
# Uso:  bash scripts/demo/02-mesas.sh
#
# La slide 9 necesita que la mesa 2 tenga UNA sola vacante. Si no la tiene, hay
# que correr 00-reset.sh.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

banner "02 - MESAS, CUENTAS, TOPOLOGIA Y CHECKLIST"

TOKEN=$(tok login "{\"email\":\"gm@tfinder.dev\",\"password\":\"$CLAVE\"}")
TOKEN_ADMIN=$(tok login "{\"email\":\"admin@tfinder.dev\",\"password\":\"$CLAVE\"}")

seccion "estado de las mesas"
esperado "mesa 1 en 2/4 y mesa 2 en 3/4"
curl -s localhost:8001/api/v1/mesas \
  | jq -r '.[] | "  mesa \(.id): \(.nombre)  \(.jugadores_actuales)/\(.jugadores_max)  \(.estado)"'
chequear "mesa 1" \
  "$(curl -s localhost:8001/api/v1/mesas/1 | jq -r '"\(.jugadores_actuales)/\(.jugadores_max)"')" "2/4"
chequear "mesa 2" \
  "$(curl -s localhost:8001/api/v1/mesas/2 | jq -r '"\(.jugadores_actuales)/\(.jugadores_max)"')" "3/4"

# Si las mesas no estan en el estado de demostracion, el problema casi seguro es
# que ya se corrio la demo. El reset lo resuelve.
if [ "$FALLOS" -gt 0 ]; then
  banner "EL ESTADO NO ES EL DE DEMOSTRACION"
  nota "Las diferencias de arriba son esperadas si ya corriste 04-concurrencia.sh"
  nota "o 09-recorrido.sh: esas demos consumen vacantes a proposito."
  echo
  echo "    bash scripts/demo/00-reset.sh && bash scripts/demo/01-preparacion.sh"
fi

seccion "quien esta en cada mesa"
esperado "mesa 1 sin jugador3@, mesa 2 con los tres jugadores"
for i in 1 2; do
  printf '  mesa %s -> ' "$i"
  p "$TOKEN" GET "localhost:8001/api/v1/mesas/$i/miembros" | jq -r '[.miembros[].email] | join(", ")'
done

seccion "ids de las cuentas que usa la demo"
esperado "jugador3@ = 5 y gm@ = 2 con el seed limpio"
cuenta jugador3@tfinder.dev
cuenta gm@tfinder.dev

seccion "topologia de la mensajeria"
esperado "tres colas con un consumidor cada una, y dlq.general con cero"
docker compose exec -T rabbitmq rabbitmqctl list_queues -p / name durable messages_ready consumers 2>/dev/null \
  | grep -vE 'Timeout|Listing queues|^$'
chequear "consumidores de dlq.general" \
  "$(docker compose exec -T rabbitmq rabbitmqctl list_queues -p / name consumers 2>/dev/null \
     | awk '$1=="dlq.general"{print $2}')" "0"

seccion "bindings: exchange hacia cola"
esperado "tfinder.events a tres colas, y tfinder.dlx a la DLQ"
docker compose exec -T rabbitmq rabbitmqctl list_bindings -p / source_name destination_name routing_key 2>/dev/null \
  | grep -E '^tfinder'

seccion "checklist antes de hablar"
chequear "cola de fallidos vacia" \
  "$(p "$TOKEN_ADMIN" GET 'localhost:8004/api/v1/dlq?limite=1')" "[]"
chequear "el token sigue sirviendo" \
  "$(pc "$TOKEN" GET localhost:8001/api/v1/auth/me)" "200"
chequear "frontend" "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5173/)" "200"

resumen
echo
echo "  Siguiente:  bash scripts/demo/03-arquitectura.sh"
