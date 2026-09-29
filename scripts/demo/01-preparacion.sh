#!/usr/bin/env bash
# Verifica los cuatro servicios, el frontend y obtiene los cuatro tokens.
#
# Uso:  bash scripts/demo/01-preparacion.sh
#
# Cada script pide los tokens que necesita por su cuenta, asi que se puede
# correr este en cualquier momento. Los tokens duran 24 h.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

banner "01 - PREPARACION: SERVICIOS, FRONTEND Y TOKENS"

seccion "los cuatro servicios"
esperado "los cuatro 200 con postgres, redis y rabbitmq en true"
for puerto in 8001 8002 8003 8004; do
  printf '  %s -> ' "$puerto"
  curl -s -w ' [%{http_code}]\n' "http://127.0.0.1:$puerto/ready"
done
chequear "8001 listo" "$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8001/ready)" "200"
chequear "8002 listo" "$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8002/ready)" "200"
chequear "8003 listo" "$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8003/ready)" "200"
chequear "8004 listo" "$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8004/ready)" "200"

seccion "el frontend responde"
esperado ":5173 en 200, y el proxy hacia las APIs tambien"
chequear "frontend :5173" \
  "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5173/)" "200"
chequear "proxy :5173/mesas-api" \
  "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5173/mesas-api/api/v1/mesas)" "200"

seccion "los cuatro tokens"
esperado "los cuatro con longitud distinta de cero (243 / 251 / 260 / 260)"
TOKEN=$(tok login "{\"email\":\"gm@tfinder.dev\",\"password\":\"$CLAVE\"}")
TOKEN_ADMIN=$(tok login "{\"email\":\"admin@tfinder.dev\",\"password\":\"$CLAVE\"}")
TOKEN_A=$(alta racedemo_a@tfinder.dev "Race A")
TOKEN_B=$(alta racedemo_b@tfinder.dev "Race B")
printf '  TOKEN=%s  TOKEN_ADMIN=%s  TOKEN_A=%s  TOKEN_B=%s\n' \
  "${#TOKEN}" "${#TOKEN_ADMIN}" "${#TOKEN_A}" "${#TOKEN_B}"
[ "${#TOKEN}" -gt 0 ] && ok "token de gm" || fallo "token de gm vacio"
[ "${#TOKEN_ADMIN}" -gt 0 ] && ok "token de admin" || fallo "token de admin vacio"
[ "${#TOKEN_A}" -gt 0 ] && ok "token de racedemo_a" || fallo "token de racedemo_a vacio"
[ "${#TOKEN_B}" -gt 0 ] && ok "token de racedemo_b" || fallo "token de racedemo_b vacio"

seccion "un solo token sirve en los cuatro servicios"
esperado "200 en los cuatro: no hace falta autenticarse por servicio"
p "$TOKEN" GET localhost:8001/api/v1/auth/me | jq -c .; echo
for ruta in 8002/api/v1/builds/1 8003/api/v1/feed 8004/api/v1/notificaciones; do
  chequear "$ruta" "$(pc "$TOKEN" GET "localhost:$ruta")" "200"
done

resumen
echo
echo "  Siguiente:  bash scripts/demo/02-mesas.sh"
