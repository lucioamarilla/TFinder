#!/usr/bin/env bash
# Slide 18. Las pruebas, de las dos capas.
#
# Uso:  bash scripts/demo/11-testing.sh
#
# Las de integracion levantan bases _test y un vhost propio, asi que no tocan
# los datos de la demostracion. Tarda unos 20 s.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

banner "SLIDE 18 - TESTING"

seccion "frontend: unitarias"
esperado "15 casos en 3 archivos"
(cd tfinder-vue && npm run test:unit 2>&1 | tail -6)
chequear "unitarias de frontend" \
  "$(cd tfinder-vue && npm run test:unit 2>&1 | grep -oE 'Tests +[0-9]+ passed' | grep -oE '[0-9]+')" "15"

seccion "frontend: integracion"
esperado "7 casos en 2 archivos"
(cd tfinder-vue && npm run test:integration 2>&1 | tail -4)
chequear "integracion de frontend" \
  "$(cd tfinder-vue && npm run test:integration 2>&1 | grep -oE 'Tests +[0-9]+ passed' | grep -oE '[0-9]+')" "7"

seccion "backend: unitarias"
esperado "50 passed"
venv/bin/python -m pytest -m unit -q 2>&1 | tail -1
chequear "unitarias de backend" \
  "$(venv/bin/python -m pytest -m unit -q 2>&1 | grep -oE '[0-9]+ passed' | grep -oE '^[0-9]+')" "50"

seccion "backend: integracion"
esperado "80 passed, contra PostgreSQL, Redis y RabbitMQ reales"
venv/bin/python -m pytest -m integration -q 2>&1 | tail -1
chequear "integracion de backend" \
  "$(venv/bin/python -m pytest -m integration -q 2>&1 | grep -oE '[0-9]+ passed' | grep -oE '^[0-9]+')" "80"

banner "EL TOTAL"
esperado "22 de frontend + 130 de backend = 152"
printf '  frontend  15 unitarias + 7 integracion  =  22\n'
printf '  backend   50 unitarias + 80 integracion = 130\n'
printf '  %sTOTAL%s                                      152\n' "$TITULO" "$FIN"

seccion "el desglose de los archivos de frontend"
grep -c 'it(' tfinder-vue/tests/unit/feature-gating.spec.js | sed 's/^/  feature-gating.spec.js  /'
grep -c 'it(' tfinder-vue/tests/unit/components.spec.js    | sed 's/^/  components.spec.js      /'
nota "inventory.spec.js no tiene 4 'it(' literales: los genera con un helper"
nota "invocado una vez por cada carpeta. Suman 4 casos igual."

resumen
echo
echo "  Siguiente:  bash scripts/demo/12-qr.sh   (opcional, si sobra tiempo)"
