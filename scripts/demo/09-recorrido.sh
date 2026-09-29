#!/usr/bin/env bash
# Slide 16. El recorrido de la aplicacion, en ocho pasos, sobre datos reales.
#
# Uso:  bash scripts/demo/09-recorrido.sh
#
# Es re-ejecutable. En la primera corrida la mesa 1 va de 2/4 a 3/4; en la
# segunda ya esta en 3/4, y el paso 3 vuelve a sumar porque la cuenta ya es
# miembro. Si llega a 4/4, corre 00-reset.sh.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

TOKEN=$(tok login "{\"email\":\"gm@tfinder.dev\",\"password\":\"$CLAVE\"}")
TOKEN_ADMIN=$(tok login "{\"email\":\"admin@tfinder.dev\",\"password\":\"$CLAVE\"}")
TOKEN_J3=$(tok login "{\"email\":\"jugador3@tfinder.dev\",\"password\":\"$CLAVE\"}")

banner "SLIDE 16 - RECORRIDO DE LA APLICACION EN 8 PASOS"

# ----------------------------------------------------------------- paso 1 ----
banner "PASO 1 - El listado, con el filtro 'con vacantes'"
esperado "las mesas abiertas que aun tienen lugar"
curl -s localhost:8001/api/v1/mesas | jq -r '
  .[] | select(.estado=="abierta" and .jugadores_actuales < .jugadores_max)
  | "  \(.id)  \(.nombre)  \(.jugadores_actuales)/\(.jugadores_max)  \(.sistema)"'
nota "El filtro es del CLIENTE: GET /mesas no acepta parametros de consulta y"
nota "devuelve todas las mesas. Lo que viene de la API son los numeros."
nota "La mesa 3 no aparece: esta cerrada con 0 jugadores, no tiene vacantes libres."

# ----------------------------------------------------------------- paso 2 ----
banner "PASO 2 - El detalle de una mesa"
esperado "el contador actual y el maximo, que es lo que decide si hay lugar"
curl -s localhost:8001/api/v1/mesas/1 | jq -c '{id,nombre,jugadores_actuales,jugadores_max,estado}'

# ----------------------------------------------------------------- paso 3 ----
banner "PASO 3 - Unirse: jugador3@ sobre la mesa 1"
esperado "201, con la fila de la solicitud"
ANTES=$(curl -s localhost:8001/api/v1/mesas/1 | jq -r '.jugadores_actuales')
chequear_uno_de "mesa 1 antes de unirse" "$ANTES" 2 3
avisar_sin_vacantes 1 "Mesa Demo Abierta" || nota "el paso 3 va a fallar por falta de vacante"
# Una sola llamada: el codigo y el cuerpo salen de la misma peticion. Hacer una
# segunda para chequear el codigo sumaria otro miembro y moveria el contador.
UNION=$(p "$TOKEN_J3" POST localhost:8001/api/v1/mesas/1/solicitudes \
  -H "Idempotency-Key: guia-$(date +%s)" -H 'Content-Type: application/json' \
  -d '{}' -w '\n[%{http_code}]')
printf '  %s\n' "$(printf '%s\n' "$UNION" | head -1)"
chequear "codigo de la union" "$(printf '%s\n' "$UNION" | tail -1 | tr -d '[]')" "201"

# ----------------------------------------------------------------- paso 4 ----
banner "PASO 4 - El contador se movio en la base"
esperado "un jugador mas que antes"
# Se consulta el DETALLE y no el listado: el listado va cacheado y puede mostrar
# el contador viejo hasta 60 s. El detalle y la base estan al dia.
DESPUES=$(curl -s localhost:8001/api/v1/mesas/1 | jq -r '.jugadores_actuales')
chequear "mesa 1 despues" "$DESPUES" "$((ANTES + 1))"
curl -s localhost:8001/api/v1/mesas/1 | jq -r '"  \(.nombre): \(.jugadores_actuales)/\(.jugadores_max)"'
docker compose exec -T postgres psql -U tfinder -d mesas_db \
  -c "SELECT id, nombre, jugadores_actuales, jugadores_max FROM mesas ORDER BY id;"

# ----------------------------------------------------------------- paso 5 ----
banner "PASO 5 - La notificacion, y la prueba de que no es un setTimeout"
esperado "el mensaje entra por SSE despues del evento, y queda guardado en la base"

# Mesa propia para este paso, para que el script sea re-ejecutable.
MESA_SSE=$(mesa_de_prueba 4 "Mesa SSE")
[ -n "$MESA_SSE" ] || { fallo "no se pudo crear la mesa para el paso 5"; }

# El stream se abre ANTES de disparar el evento, para que se vea llegar.
(timeout 8 curl -sN localhost:8004/api/v1/notificaciones/stream \
   -H "Authorization: Bearer $TOKEN_J3" > /tmp/tf-sse.txt 2>&1 &)
sleep 1

p "$TOKEN_J3" POST "localhost:8001/api/v1/mesas/$MESA_SSE/solicitudes" \
  -H "Idempotency-Key: sse-$(date +%s)" -H 'Content-Type: application/json' \
  -d '{}' -w '  disparo -> %{http_code}\n'
sleep 4

seccion "lo que llego por el stream"
cat /tmp/tf-sse.txt
chequear "llego un evento por SSE" \
  "$(grep -c 'solicitud' /tmp/tf-sse.txt | tr -d ' ')" "1"

seccion "lo que quedo guardado"
curl -s "localhost:8004/api/v1/notificaciones?solo_no_leidas=true" \
  -H "Authorization: Bearer $TOKEN_J3" | jq -c '.[0]'
chequear "mensaje de la notificacion" \
  "$(p "$TOKEN_J3" GET 'localhost:8004/api/v1/notificaciones?solo_no_leidas=true' \
     | jq -r '.[0].mensaje // ""')" "Solicitud aceptada"

# ----------------------------------------------------------------- paso 6 ----
banner "PASO 6 - Matchmaking: el TTL de Redis contandose en vivo"
esperado "expira_en 120, y el ttl_restante bajando"

MM=$(p "$TOKEN" POST localhost:8001/api/v1/matchmaking/1/abrir)
echo "  $MM" | jq -c .
MMID=$(echo "$MM" | jq -r '.matchmaking_id // ""')
[ -n "$MMID" ] && ok "matchmaking_id=$MMID" || fallo "la apertura no devolvio matchmaking_id"

for i in 1 2 3; do
  printf '  t+%ss ' "$((i * 2))"
  curl -s "localhost:8001/api/v1/matchmaking/$MMID/estado"; echo
  sleep 2
done

seccion "el mismo endpoint con un rol que no es gm"
esperado "403 Rol insuficiente"
p "$TOKEN_J3" POST localhost:8001/api/v1/matchmaking/1/abrir -w '  [%{http_code}]\n'

# ----------------------------------------------------------------- paso 7 ----
banner "PASO 7 - /encuentros: una pantalla que NO toca el backend"
esperado "0 imports de la capa de API y 0 endpoints declarados"
printf '  imports de @/api en la vista      : %s\n' "$(grep -c '@/api' tfinder-vue/src/views/EncuentrosView.vue)"
printf '  referencias en el cliente de la API: %s\n' "$(grep -c 'encuentros' tfinder-vue/src/api/endpoints.js)"
chequear "imports de la API en la vista" "$(grep -c '@/api' tfinder-vue/src/views/EncuentrosView.vue)" "0"
chequear "endpoints declarados"           "$(grep -c 'encuentros' tfinder-vue/src/api/endpoints.js)" "0"
seccion "de donde sale el resultado"
grep -n 'Math.random\|BESTIARIO' tfinder-vue/src/views/EncuentrosView.vue | head -3
nota "El calculo es del cliente. La funcion esta detras del feature flag activo y"
nota "aun asi no necesita backend. Es el caso honesto: no toda pantalla es una consulta."

# ----------------------------------------------------------------- paso 8 ----
banner "PASO 8 - /admin/estadisticas: diez pantallas que son datos de demostracion"
esperado "10 JSON estaticos, latencia simulada, y 0 llamadas a la API"
sed -n '1,13p' tfinder-vue/src/services/admin.js
chequear "JSON de admin importados" \
  "$(grep -c "from '@/data/admin/" tfinder-vue/src/services/admin.js)" "10"
chequear "llamadas a la API en vistas admin" \
  "$(grep -rl '@/api' tfinder-vue/src/views/ | grep -c admin || true)" "0"

seccion "pero la frontera de roles del backend es real"
esperado "200 con admin, 403 con gm, y la DLQ vacia"
p "$TOKEN_ADMIN" GET localhost:8001/api/v1/auth/admin-only -w '  [%{http_code}]\n'
chequear "admin" "$(pc "$TOKEN_ADMIN" GET localhost:8001/api/v1/auth/admin-only)" "200"
p "$TOKEN" GET localhost:8001/api/v1/auth/admin-only -w '  [%{http_code}]\n'
chequear "gm"   "$(pc "$TOKEN"      GET localhost:8001/api/v1/auth/admin-only)" "403"
p "$TOKEN_ADMIN" GET 'localhost:8004/api/v1/dlq?limite=1' -w '  [%{http_code}]\n'

resumen
echo
echo "  Siguiente:  bash scripts/demo/10-gating.sh"
