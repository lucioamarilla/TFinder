#!/usr/bin/env bash
# Demo extra: el QR de un solo uso.
#
# Uso:  bash scripts/demo/12-qr.sh
#
# Sirve para cuando sobra tiempo. El GETDEL de Redis es atomico: el primer
# GETDEL borra, el segundo devuelve nada y el backend responde 409.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

banner "DEMO EXTRA - EL QR DE UN SOLO USO"

TOKEN=$(tok login "{\"email\":\"gm@tfinder.dev\",\"password\":\"$CLAVE\"}")
# El usuario_id del cuerpo tiene que ser el del EMISOR del QR: el QR ata al
# que lo pidio con su propia asistencia.
ID_EMISOR=$(docker compose exec -T postgres psql -U tfinder -d mesas_db -tAc \
  "select id from usuarios where email='gm@tfinder.dev'" | tr -d '\r' | grep -oE '[0-9]+' | head -1)
[ -n "$ID_EMISOR" ] && printf '  emisor: gm@tfinder.dev (usuario_id %s)\n' "$ID_EMISOR" \
  || fallo "no se encontro el id de gm@tfinder.dev"

seccion "1. emitir el QR"
esperado "un qr_data y expira_en_seg 600"
QR=$(p "$TOKEN" POST localhost:8001/api/v1/sesiones/1/qr | jq -r '.qr_data // ""')
printf '  qr_data=%s...\n' "${QR:0:40}"
[ -n "$QR" ] && ok "QR emitido" || fallo "no se emitio el QR"

seccion "2. validar: la primera vez registra la asistencia"
esperado '200 con {"asistencia":"registrada"}'
# Una sola llamada: el cuerpo y el codigo salen de la misma peticion, porque la
# segunda validacion del mismo codigo ya da 409.
PRIMERA=$(p "$TOKEN" POST localhost:8001/api/v1/sesiones/1/qr/validar \
  -H 'Content-Type: application/json' \
  -d "{\"usuario_id\": $ID_EMISOR, \"qr_data\": \"$QR\"}" -w '\n[%{http_code}]')
printf '  %s\n' "$(printf '%s\n' "$PRIMERA" | head -1)"
chequear "primera validacion" "$(printf '%s\n' "$PRIMERA" | tail -1 | tr -d '[]')" "200"

seccion "3. la MISMA validacion otra vez, con el mismo codigo"
esperado "409 con 'QR vencido o ya utilizado'"
p "$TOKEN" POST localhost:8001/api/v1/sesiones/1/qr/validar \
  -H 'Content-Type: application/json' \
  -d "{\"usuario_id\": $ID_EMISOR, \"qr_data\": \"$QR\"}" -w '  [%{http_code}]\n'
chequear "segunda validacion" \
  "$(pc "$TOKEN" POST localhost:8001/api/v1/sesiones/1/qr/validar \
     -H 'Content-Type: application/json' \
     -d "{\"usuario_id\": $ID_EMISOR, \"qr_data\": \"$QR\"}")" "409"

seccion "la clave en Redis se consume, no solo expira"
esperado "sin claves qr:* para esa sesion y ese usuario"
restantes=$(docker compose exec -T redis redis-cli --scan --pattern "qr:sesion:1:$ID_EMISOR" | tr -d '\r' | grep -c . || true)
chequear "claves qr:* colgadas" "$restantes" "0"

seccion "una sola fila por sesion y usuario"
docker compose exec -T postgres psql -U tfinder -d mesas_db \
  -c "SELECT * FROM asistencias WHERE usuario_id = $ID_EMISOR ORDER BY id DESC LIMIT 3;"

nota "El GETDEL lee y borra en una sola operacion atomica: dos validaciones"
nota "simultaneas del mismo codigo no pueden pasar las dos."

resumen
echo
echo "  Demo extra completa. No hay un siguiente paso obligatorio."
