#!/usr/bin/env bash
# Slide 15. El replay de idempotencia.
#
# Uso:  bash scripts/demo/08-idempotencia.sh
#
# Crea su propia mesa de prueba, para poder correrlo las veces que haga falta.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

banner "SLIDE 15 - IDEMPOTENCIA: EL REPLAY"

TOKEN=$(tok login "{\"email\":\"gm@tfinder.dev\",\"password\":\"$CLAVE\"}")
MESA=$(mesa_de_prueba 6 "Mesa Idempotencia")
if [ -z "$MESA" ]; then
  fallo "no se pudo crear la mesa de prueba"
  resumen; exit 1
fi
printf '  mesa de prueba: id %s, con 6 vacantes\n' "$MESA"
KEY="idem-demo-$(date +%s)"
printf '  Idempotency-Key=%s\n\n' "$KEY"

seccion "1. primera llamada"
primera=$(p "$TOKEN" POST localhost:8001/api/v1/mesas/$MESA/solicitudes \
  -H "Idempotency-Key: $KEY" -H 'Content-Type: application/json' -d '{}')
printf '  %s\n' "$primera"
ID1=$(echo "$primera" | jq -r '.id // ""')
[ -n "$ID1" ] && ok "creo la fila $ID1" || fallo "no creo ninguna fila"

seccion "2. replay: MISMA clave, misma peticion"
esperado "el mismo id y la misma fecha, byte a byte"
segunda=$(p "$TOKEN" POST localhost:8001/api/v1/mesas/$MESA/solicitudes \
  -H "Idempotency-Key: $KEY" -H 'Content-Type: application/json' -d '{}')
printf '  %s\n' "$segunda"
ID2=$(echo "$segunda" | jq -r '.id // ""')
chequear "id del replay" "$ID2" "$ID1"
[ "$primera" = "$segunda" ] && ok "cuerpo identico al de la primera" \
  || fallo "el replay devolvio un cuerpo distinto"

seccion "3. con OTRA clave: si es una operacion nueva, crea otra fila"
tercera=$(p "$TOKEN" POST localhost:8001/api/v1/mesas/$MESA/solicitudes \
  -H "Idempotency-Key: ${KEY}-bis" -H 'Content-Type: application/json' -d '{}')
printf '  %s\n' "$tercera"
ID3=$(echo "$tercera" | jq -r '.id // ""')
[ -n "$ID3" ] && [ "$ID3" != "$ID1" ] && ok "fila nueva: id $ID3" \
  || fallo "la clave nueva no creo una fila nueva"

seccion "4. donde vive la clave: una sola fila en Postgres, TTL de 24 h en Redis"
esperado "una unica fila con $KEY, y la clave en Redis con TTL 86400"
docker compose exec -T postgres psql -U tfinder -d mesas_db \
  -c "SELECT id, mesa_id, usuario_id, estado, idem_key FROM solicitudes_uniones WHERE idem_key LIKE 'idem-demo-%' ORDER BY id DESC LIMIT 3;"

chequear "filas con esa clave en Postgres" \
  "$(docker compose exec -T postgres psql -U tfinder -d mesas_db -tAc \
     "select count(*) from solicitudes_uniones where idem_key='$KEY'")" "1"

chequear "TTL de la clave en Redis" \
  "$(docker compose exec -T redis redis-cli TTL "idem:solicitud:$KEY" | tr -d '\r')" "86400"

docker compose exec -T redis redis-cli --scan --pattern 'idem:*'

seccion "el cupo: el replay NO consumio una segunda vacante"
esperado "la mesa subio en 2 de 6, no en 3: la clave repetida no ocupa otra"
curl -s "localhost:8001/api/v1/mesas/$MESA" | jq -r '"  \(.nombre): \(.jugadores_actuales)/\(.jugadores_max)"'

seccion "el replay sigue siendo el mismo id DESPUES de otras operaciones"
esperado "la clave original sigue devolviendo la misma fila, aunque la base haya cambiado"
p "$TOKEN" POST localhost:8001/api/v1/mesas/$MESA/solicitudes \
  -H "Idempotency-Key: $KEY" -H 'Content-Type: application/json' -d '{}' -w '  [%{http_code}]\n'
chequear "el replay tardio devuelve la fila original" \
  "$(p "$TOKEN" POST localhost:8001/api/v1/mesas/$MESA/solicitudes \
     -H "Idempotency-Key: $KEY" -H 'Content-Type: application/json' -d '{}' \
     | jq -r '.id // ""')" "$ID1"

seccion "y con una clave distinta sobre una mesa con lugar, si es operacion nueva"
esperado "201 con una fila nueva: la idempotencia la decide la clave, no el usuario"
p "$TOKEN" POST localhost:8001/api/v1/mesas/$MESA/solicitudes \
  -H "Idempotency-Key: ${KEY}-otra" -H 'Content-Type: application/json' -d '{}' -w '  [%{http_code}]\n'
nota "Sin el header Idempotency-Key el backend guardaria idem_key NULL y cada"
nota "llamada seria una operacion nueva: por eso la clave tiene que ser estable."

resumen
echo
echo "  Siguiente:  bash scripts/demo/09-recorrido.sh"
