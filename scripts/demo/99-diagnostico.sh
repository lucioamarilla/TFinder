#!/usr/bin/env bash
# Por que fallo algo. Corre esto antes que probar cualquier otra cosa.
#
# Uso:  bash scripts/demo/99-diagnostico.sh
#
# Los tres motivos mas comunes de un 401, en orden de probabilidad:
#   1. el token es viejo, de mas de 24 h
#   2. Redis quedo pausado por la slide 12 sin restaurar
#   3. se hizo docker compose down -v DESPUES de sacar el token
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

banner "99 - DIAGNOSTICO"

seccion "1. el token de gm: rol, tipo, vigencia y sesion en Redis"
TOKEN=$(tok login "{\"email\":\"gm@tfinder.dev\",\"password\":\"$CLAVE\"}")
if [ -z "$TOKEN" ]; then
  fallo "no se pudo ni sacar un token nuevo: revisa que el stack este arriba"
else
  PAYLOAD=$(decodificar "$TOKEN")
  if [ -n "$PAYLOAD" ]; then
    printf '  rol=%s  tipo=%s  jti=%s  exp=%s (epoch)\n' \
      "$(echo "$PAYLOAD" | jq -r .rol)" \
      "$(echo "$PAYLOAD" | jq -r .tipo)" \
      "$(echo "$PAYLOAD" | jq -r .jti)" \
      "$(echo "$PAYLOAD" | jq -r .exp)"
    VIGENTE=$(echo "$PAYLOAD" | jq -r '.exp - now | floor')
    if [ "$VIGENTE" -gt 0 ]; then ok "el token vence en $((VIGENTE / 60)) minutos"
    else fallo "el token EXPIRO hace $((VIGENTE / -60)) minutos. Volve a correr 01."; fi
  else
    fallo "no se pudo leer el contenido del token"
  fi

  JTI=$(jti_de "$TOKEN")
  if [ -n "$JTI" ]; then
    TTL=$(docker exec tfinder-redis redis-cli TTL "sesion:$JTI" 2>/dev/null | tr -d '\r')
    if [ "${TTL:-0}" -gt 0 ] 2>/dev/null; then ok "la sesion vive en Redis, TTL ${TTL}s"
    else fallo "NO hay sesion:$JTI en Redis: el token esta revocado o Redis se reinicio. Corre 01."; fi
  fi
fi

seccion "2. los secretos JWT coinciden entre los cuatro servicios"
esperado "los cuatro con el mismo valor (dev-secret con el compose de ejemplo)"
for c in tfinder-mesas-api tfinder-notif-api tfinder-builds-api tfinder-feed-api; do
  printf '  %-22s -> %s\n' "$c" "$(docker exec "$c" printenv JWT_SECRET 2>/dev/null | tr -d '\n')"
done
UNICOS=$(for c in tfinder-mesas-api tfinder-notif-api tfinder-builds-api tfinder-feed-api; do
  docker exec "$c" printenv JWT_SECRET; done | sort -u | grep -c . || true)
chequear "valores distintos de JWT_SECRET" "$UNICOS" "1"

seccion "3. el estado de la infraestructura"
docker compose ps --format '{{.Name}}  {{.Status}}'
seccion "las cuatro sondas de salud"
for puerto in 8001 8002 8003 8004; do
  printf '  %s -> ' "$puerto"
  curl -s -m 5 -w ' [%{http_code}]\n' "http://127.0.0.1:$puerto/ready" || echo " [sin respuesta]"
done

seccion "4. Redis esta vivo y con sesiones"
docker exec tfinder-redis redis-cli PING 2>&1 | sed 's/^/  /'
docker exec tfinder-redis redis-cli --scan --pattern 'sesion:*' 2>/dev/null | head -5 | sed 's/^/  /'
NOTA_SES=$(docker exec tfinder-redis redis-cli --scan --pattern 'sesion:*' 2>/dev/null | grep -c . || true)
[ "$NOTA_SES" -gt 0 ] && ok "$NOTA_SES sesiones en Redis" \
  || fallo "no hay sesiones en Redis.Casi seguro: se hizo down -v despues de sacar los tokens."

seccion "5. las cuentas de la demo"
docker compose exec -T postgres psql -U tfinder -d mesas_db -tAc \
  "select '  '||email||'  rol='||rol from usuarios where email ilike 'racedemo%' or email ilike '%tfinder.dev' order by email;"

seccion "6. el estado de las mesas"
curl -s -m 5 localhost:8001/api/v1/mesas \
  | jq -r '.[] | "  mesa \(.id): \(.nombre)  \(.jugadores_actuales)/\(.jugadores_max)  \(.estado)"' 2>/dev/null
nota "La slide 9 necesita la mesa 2 en 3/4. Si esta en 4/4, corre 00-reset.sh."

seccion "7. los ultimos logs de notif-api"
docker compose logs notif-api --tail 12 --no-log-prefix 2>/dev/null | sed 's/^/  /'

banner "SI ALGO SIGUE FALLANDO"
cat <<'FIN'
  La salida mas simple, en este orden:

    bash scripts/demo/00-reset.sh
    bash scripts/demo/01-preparacion.sh
    bash scripts/demo/02-mesas.sh

  Si 01 dice que los tokens estan vacios, el problema es la autenticacion.
  Si 01 dice 200 en todo y 02 dice 401, el problema son las sesiones de Redis.
  Si 02 dice que la mesa 2 no esta en 3/4, falta el reset.
FIN

resumen
