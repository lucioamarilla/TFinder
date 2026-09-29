#!/usr/bin/env bash
# Slide 12. Modo degradado y correlacion de punta a punta.
#
# Uso:  bash scripts/demo/07-seguridad.sh
#
# IMPORTANTE: la pausa de Redis esta apareada con la restauracion por un trap
# en EXIT. Si se interrumpe el script con Ctrl-C, Redis queda despausado igual.
# Sin eso, todo lo que se corre despues devuelve 401 por falta de sesiones.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

TOKEN=$(tok login "{\"email\":\"gm@tfinder.dev\",\"password\":\"$CLAVE\"}")
TOKEN_ADMIN=$(tok login "{\"email\":\"admin@tfinder.dev\",\"password\":\"$CLAVE\"}")

redis_en_pausa=0
restaurar_redis() {
  if [ "$redis_en_pausa" -eq 1 ]; then
    docker compose unpause redis > /dev/null 2>&1 || true
    redis_en_pausa=0
  fi
}
trap restaurar_redis EXIT INT TERM

banner "SLIDE 12 - MODO DEGRADADO"

seccion "pausa de Redis: que pasa con las sondas de salud"
esperado "/ready en 503 con el mapa de dependencias, /live en 200"

docker compose pause redis > /dev/null 2>&1
redis_en_pausa=1

curl -s -w '  [%{http_code}]\n' localhost:8004/ready
curl -s -w '  [%{http_code}]\n' localhost:8004/live

chequear "/ready con Redis caido" "$(curl -s -o /dev/null -w '%{http_code}' localhost:8004/ready)" "503"
chequear "/live con Redis caido"  "$(curl -s -o /dev/null -w '%{http_code}' localhost:8004/live)"  "200"

docker compose unpause redis > /dev/null 2>&1
redis_en_pausa=0
sleep 3
seccion "tras restaurar Redis"
esperado "vuelve a \"estado\":\"listo\""
curl -s -w '  [%{http_code}]\n' localhost:8004/ready
chequear "/ready restaurado" "$(curl -s -o /dev/null -w '%{http_code}' localhost:8004/ready)" "200"


banner "SLIDE 12 - CORRELACION DE PUNTA A PUNTA"

# Usa la MESA 3, que esta vacia, para no robarle el cupo a la slide 16.
seccion "una peticion a mesas-api con un identificador propio"
esperado "el mismo correlation_id en los logs y en la base de notif_api"

CID="demo-corr-$(date +%H%M%S)"
printf '  correlation_id=%s\n' "$CID"
p "$TOKEN" POST localhost:8001/api/v1/mesas/3/solicitudes \
  -H "X-Correlation-Id: $CID" -H "Idempotency-Key: k-$CID" \
  -H 'Content-Type: application/json' -d '{}' -w '  solicitud -> %{http_code}\n'

seccion "en los logs del servicio que recibio la peticion"
docker compose logs mesas-api --no-log-prefix 2>/dev/null | grep "$CID" | tail -2
chequear "el identificador aparece en los logs" \
  "$(docker compose logs mesas-api --no-log-prefix 2>/dev/null | grep -c "$CID" | tr -d ' ')" "2"

seccion "en la base de datos de notif_api, otro proceso y otra base"
esperado "una entrada con el mismo correlationId, con entidad mesa.aceptada"
sleep 2
EVENTO=$(p "$TOKEN_ADMIN" GET "localhost:8004/api/v1/event-log?correlation_id=$CID")
echo "$EVENTO" | jq -c .
chequear "el identificador llego al event-log" \
  "$(echo "$EVENTO" | jq -r '.[0].correlationId // ""')" "$CID"
chequear "entidad registrada" \
  "$(echo "$EVENTO" | jq -r '.[0].entidadTipo // ""')" "mesa.aceptada"

seccion "el mismo token sirve en los cuatro servicios con la sesion viva"
esperado "200 en los cuatro"
for ruta in 8001/api/v1/auth/me 8002/api/v1/builds/1 8003/api/v1/feed 8004/api/v1/notificaciones; do
  chequear "$ruta" "$(pc "$TOKEN" GET "localhost:$ruta")" "200"
done

resumen
echo
echo "  Siguiente:  bash scripts/demo/08-idempotencia.sh"
