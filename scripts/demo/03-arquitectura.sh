#!/usr/bin/env bash
# Slides 8, 13 y 14. Las tres sostienen el mismo argumento: cuatro servicios
# independientes, con la misma forma de contrato.
#
# Uso:
#   bash scripts/demo/03-arquitectura.sh            # las tres
#   bash scripts/demo/03-arquitectura.sh bases      # solo la slide 8
#   bash scripts/demo/03-arquitectura.sh rutas      # solo la slide 13
#   bash scripts/demo/03-arquitectura.sh errores    # solo la slide 14
#
# Estas tres slides estan separadas en el tiempo por las 9 a la 12, asi que
# en la presentacion se corre una parte por vez.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

PARTE="${1:-todas}"

bases() {
  banner "SLIDE 8 - ARQUITECTURA: LAS CUATRO BASES"
  esperado "builds_db, feed_db, mesas_db y notif_db. No existe una base 'tfinder'."
  # El -d postgres es obligatorio: sin base, psql intenta conectarse a una llamada
  # como el usuario y falla con database "tfinder" does not exist.
  docker compose exec -T postgres psql -U tfinder -d postgres -c "\l" \
    | grep -E " (mesas|builds|feed|notif)_db " | awk '{print $1}'
  chequear "bases encontradas" \
    "$(docker compose exec -T postgres psql -U tfinder -d postgres -tAc \
       "select count(*) from pg_database where datname in ('mesas_db','builds_db','feed_db','notif_db')")" \
    "4"
}

rutas() {
  banner "SLIDE 13 - FRONTEND: RUTAS Y VISTAS"
  esperado "45 rutas y 45 vistas"
  printf '  rutas:  '; grep -cE "^\s+\{ path: '" tfinder-vue/src/router/index.js
  printf '  vistas: '; find tfinder-vue/src/views -name '*.vue' | wc -l
  chequear "rutas"  "$(grep -cE "^\s+\{ path: '" tfinder-vue/src/router/index.js)" "45"
  chequear "vistas" "$(find tfinder-vue/src/views -name '*.vue' | wc -l | tr -d ' ')" "45"
}

errores() {
  banner "SLIDE 14 - EL MISMO SOBRE DE ERROR EN LOS CUATRO SERVICIOS"
  TOKEN=$(tok login "{\"email\":\"gm@tfinder.dev\",\"password\":\"$CLAVE\"}")
  esperado "los cuatro con {\"error\": {\"codigo\": 404, \"mensaje\": \"Recurso no encontrado\"}}"
  for puerto in 8001 8002 8003 8004; do
    printf '  %s -> ' "$puerto"
    p "$TOKEN" GET "localhost:$puerto/api/v1/no-existe" -w ' [%{http_code}]\n'
  done
  chequear "8001" "$(pc "$TOKEN" GET localhost:8001/api/v1/no-existe)" "404"
  chequear "8002" "$(pc "$TOKEN" GET localhost:8002/api/v1/no-existe)" "404"
  chequear "8003" "$(pc "$TOKEN" GET localhost:8003/api/v1/no-existe)" "404"
  chequear "8004" "$(pc "$TOKEN" GET localhost:8004/api/v1/no-existe)" "404"

  seccion "el error de dominio lleva un mensaje entendible"
  esperado '"Mesa 99999 no encontrada"'
  p "$TOKEN" GET localhost:8001/api/v1/mesas/99999 -w '  [%{http_code}]\n'
  chequear "error de dominio" "$(pc "$TOKEN" GET localhost:8001/api/v1/mesas/99999)" "404"
}

case "$PARTE" in
  bases)   bases ;;
  rutas)   rutas ;;
  errores) errores ;;
  todas)
    bases
    rutas
    errores
    ;;
  *)
    echo "parte desconocida: $PARTE" >&2
    echo "  uso: $0 [todas|bases|rutas|errores]" >&2
    exit 1
    ;;
esac

resumen
echo
case "$PARTE" in
  todas)   echo "  Siguiente:  bash scripts/demo/04-concurrencia.sh" ;;
  bases)   echo "  Siguiente:  bash scripts/demo/04-concurrencia.sh" ;;
  rutas)   echo "  Siguiente:  bash scripts/demo/03-arquitectura.sh errores" ;;
  errores) echo "  Siguiente:  bash scripts/demo/04-concurrencia.sh" ;;
esac
