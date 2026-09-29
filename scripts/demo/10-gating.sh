#!/usr/bin/env bash
# Slide 17. Gating: los banderas y la matriz de acceso.
#
# Uso:  bash scripts/demo/10-gating.sh
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

banner "SLIDE 17 - GATING"

seccion "los banderas, contadas desde el codigo"
esperado "20 features: 7 activas y 13 en comingSoon"
node -e "
const f = require('fs').readFileSync('tfinder-vue/src/config/features.js','utf8');
const on  = [...f.matchAll(/available: true/g)].length;
const off = [...f.matchAll(/available: false/g)].length;
console.log('  features:', on + off, '| activas:', on, '| comingSoon:', off);
"
chequear "features habilitadas" \
  "$(grep -c 'available: true' tfinder-vue/src/config/features.js)" "7"
chequear "features apagadas" \
  "$(grep -c 'available: false' tfinder-vue/src/config/features.js)" "13"

seccion "la matriz de acceso completa, ejecutada"
esperado "6 casos, todos en verde. El tercero es el caso de /encuentros."
(cd tfinder-vue && npx vitest run tests/unit/feature-gating.spec.js --reporter=verbose)
[ "${PIPESTATUS[0]}" = "0" ] && ok "la matriz de gating pasa entera" || fallo "la matriz de gating fallo"

seccion "el orden de evaluacion dentro del guard"
esperado "el feature gate retorna ANTES de que se lea to.meta.roles"
grep -n '' tfinder-vue/src/router/guard.js | sed -n '3,10p' | sed 's/^/  /'
nota "Si el chequeo de rol corriera primero, un invitado que pide /admin/estadisticas"
nota "veria la pantalla de login. Como la feature esta apagada, ve 'Proximamente':"
nota "esa pantalla todavia no existe. El flag va primero para no prometer antes de construir."

seccion "por que no se corre resolveGuard con node"
nota "guard.js importa @/config, que es un alias de Vite: node no lo resuelve."
nota "Por eso la matriz se muestra con vitest, que si entiende el alias."

resumen
echo
echo "  Siguiente:  bash scripts/demo/11-testing.sh"
