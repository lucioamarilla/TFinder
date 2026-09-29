#!/usr/bin/env bash
# Slide 9. Las dos barreras de concurrencia, una por vez.
#
# Uso:  bash scripts/demo/04-concurrencia.sh
#
# Deja la mesa 2 en 4/4. Es el unico script que la modifica, y solo una vez.
# Si ya esta en 4/4, corre 00-reset.sh antes.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

banner "SLIDE 9 - CONCURRENCIA: LAS DOS BARRERAS"

TOKEN=$(tok login "{\"email\":\"gm@tfinder.dev\",\"password\":\"$CLAVE\"}")
TOKEN_A=$(alta racedemo_a@tfinder.dev "Race A")
TOKEN_B=$(alta racedemo_b@tfinder.dev "Race B")

antes=$(curl -s localhost:8001/api/v1/mesas/2 | jq -r '"\(.nombre) \(.jugadores_actuales)/\(.jugadores_max)"')
printf '  antes: %s\n' "$antes"
[ "$antes" = "Mesa Demo Casi Llena 3/4" ] || fallo "la mesa 2 deberia estar en 3/4 y esta en '$antes'. Corre 00-reset.sh"

# ---------------------------------------------------------------- barrera 1 --
seccion "carrera: dos identidades distintas compiten por la misma vacante"
esperado "un 201 y un 409, y la mesa en 4/4. CUAL GANA ES ALEATORIO."

# Las dos peticiones salen al mismo tiempo. Cada una escribe su codigo y su
# cuerpo en un archivo propio para que la salida se lea en orden.
curl -s -o /tmp/tf-a.json -w '%{http_code}' -X POST localhost:8001/api/v1/mesas/2/solicitudes \
  -H "Authorization: Bearer $TOKEN_A" -H "Idempotency-Key: keyA" \
  -H 'Content-Type: application/json' -d '{}' > /tmp/tf-a.code &
curl -s -o /tmp/tf-b.json -w '%{http_code}' -X POST localhost:8001/api/v1/mesas/2/solicitudes \
  -H "Authorization: Bearer $TOKEN_B" -H "Idempotency-Key: keyB" \
  -H 'Content-Type: application/json' -d '{}' > /tmp/tf-b.code &
wait

a=$(cat /tmp/tf-a.code); b=$(cat /tmp/tf-b.code)
echo "  A -> HTTP $a: $(jq -c . /tmp/tf-a.json)"
echo "  B -> HTTP $b: $(jq -c . /tmp/tf-b.json)"

chequear_uno_de "codigo de A" "$a" 201 409
chequear_uno_de "codigo de B" "$b" 201 409
[ "$a" != "$b" ] && ok "exactamente uno gano" || fallo "los dos dieron el mismo codigo: no hubo carrera"
chequear "mesa 2 despues" \
  "$(curl -s localhost:8001/api/v1/mesas/2 | jq -r '"\(.jugadores_actuales)/\(.jugadores_max)"')" "4/4"

seccion "el 409 de la carrera es el lock de Redis, no el cupo agotado"
esperado '"Otra solicitud se está procesando para esta mesa, reintentá"'
jq -r 'select(.error) | "  \(.error.mensaje)"' /tmp/tf-a.json /tmp/tf-b.json 2>/dev/null | head -1

# ---------------------------------------------------------------- barrera 2 --
seccion "misma mesa, en serie, clave nueva: ahora falla la segunda barrera"
esperado '"Cupo agotado: no quedan vacantes"'
p "$TOKEN" POST localhost:8001/api/v1/mesas/2/solicitudes \
  -H "Idempotency-Key: en-serie-$(date +%s)" -H 'Content-Type: application/json' \
  -d '{}' -w '  [%{http_code}]\n'
chequear "codigo en serie" \
  "$(pc "$TOKEN" POST localhost:8001/api/v1/mesas/2/solicitudes \
     -H "Idempotency-Key: en-serie-2-$(date +%s)" -H 'Content-Type: application/json' -d '{}')" "409"

# ------------------------------------------------------------------ limpieza --
seccion "la reserva se libera sola, en el finally"
esperado "sin claves reserva:* colgadas"
colgadas=$(docker compose exec -T redis redis-cli --scan --pattern 'reserva:*' | tr -d '\r' | grep -c . || true)
chequear "reservas colgadas" "$colgadas" "0"

resumen
echo
echo "  Siguiente:  bash scripts/demo/05-redis.sh"
