#!/usr/bin/env bash
# Slide 10. Redis: la invalidacion explicita del cache.
#
# Uso:  bash scripts/demo/05-redis.sh
#
# Crea la mesa "Mesa Demo Para Invalidar", que despues aparece en el listado de
# la slide 16. Es lo esperado.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

banner "SLIDE 10 - REDIS: INVALIDACION EXPLICITA"

TOKEN=$(tok login "{\"email\":\"gm@tfinder.dev\",\"password\":\"$CLAVE\"}")

seccion "1. lectura: el listado se guarda en cache"
esperado "la clave cache:mesas:list y TTL 60 clavados"
# El DEL previo es para que el TTL salga en 60 y la demo sea determinista.
docker compose exec -T redis redis-cli DEL cache:mesas:list > /dev/null
curl -s -o /dev/null localhost:8001/api/v1/mesas
docker compose exec -T redis redis-cli --scan --pattern 'cache:*'
chequear "TTL recien escrita" \
  "$(docker compose exec -T redis redis-cli TTL cache:mesas:list | tr -d '\r')" "60"

seccion "2. escritura: la cache se borra en el acto"
esperado "sin claves cache:* despues de crear la mesa"
curl -s -o /dev/null -X POST localhost:8001/api/v1/mesas \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"nombre":"Mesa Demo Para Invalidar","sistema":"PF1e","jugadores_max":4}'

restantes=$(docker compose exec -T redis redis-cli --scan --pattern 'cache:*' | tr -d '\r' | grep -c . || true)
chequear "claves de cache tras escribir" "$restantes" "0"

seccion "por que esto importa"
nota "el TTL de 60 s es solo la red de seguridad. Lo que hace que quien crea una"
nota "mesa la vea listada de inmediato es el DEL en el camino de escritura."
nota "Si el sistema dependiera solo del TTL, la mesa aparecia un minuto despues."

seccion "los otros cinco usos de Redis, con su TTL real"
esperado "sesion 86400, idempotencia 86400, ventana de llamado 120"
docker compose exec -T redis redis-cli --scan --pattern 'sesion:*' | head -1 | while read -r k; do
  [ -n "$k" ] && printf '  %-42s TTL %s\n' "$k" "$(docker compose exec -T redis redis-cli TTL "$k" | tr -d '\r')"
done
docker compose exec -T redis redis-cli --scan --pattern 'idem:*' | head -1 | while read -r k; do
  [ -n "$k" ] && printf '  %-42s TTL %s\n' "$k" "$(docker compose exec -T redis redis-cli TTL "$k" | tr -d '\r')"
done
docker compose exec -T redis redis-cli --scan --pattern 'llamado:*' | head -1 | while read -r k; do
  [ -n "$k" ] && printf '  %-42s TTL %s\n' "$k" "$(docker compose exec -T redis redis-cli TTL "$k" | tr -d '\r')"
done
nota "(las claves de sesion, idempotencia y llamado solo existen si corriste"
nota " 01, 04 u 08 primero: se crean al usarlas, no al arrancar)"

resumen
echo
echo "  Siguiente:  bash scripts/demo/06-asincronia.sh"
