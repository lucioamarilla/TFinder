#!/usr/bin/env bash
# Libreria compartida por los scripts de la demo de 15 minutos de TFinder.
#
# Uso:  source "$(dirname "$0")/_lib.sh"
#
# No se ejecuta sola. Cada script la carga y usa sus helpers.
# Los comandos se probaron contra el stack en vivo el 2026-09-29.

# --- ubicacion ----------------------------------------------------------------
# Todos los scripts funcionan desde cualquier directorio.
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$RAIZ" || return 1

# --- salida -------------------------------------------------------------------
if [ -t 1 ]; then
  TITULO=$'\033[1;36m'; OKC=$'\033[32m'; MADC=$'\033[31m'; NOTAC=$'\033[2m'; FIN=$'\033[0m'
else
  TITULO=''; OKC=''; MADC=''; NOTAC=''; FIN=''
fi

FALLOS=0

banner()  { printf '\n%s%s%s\n' "$TITULO" "$*" "$FIN"; }
seccion() { printf '%s  -- %s%s\n' "$NOTAC" "$*" "$FIN"; }
esperado(){ printf '%s  esperado: %s%s\n' "$NOTAC" "$*" "$FIN"; }
nota()    { printf '%s  %s%s\n' "$NOTAC" "$*" "$FIN"; }
ok()      { printf '%s  OK     %s%s\n' "$OKC" "$*" "$FIN"; }
fallo()   { FALLOS=$((FALLOS + 1)); printf '%s  FALLO  %s%s\n' "$MADC" "$*" "$FIN"; }

# comparar un valor obtenido contra el verificado
chequear() { # $1=etiqueta  $2=obtenido  $3=esperado
  if [ "$2" = "$3" ]; then ok "$1: $2"
  else fallo "$1: se obtuvo '$2' y se esperaba '$3'"; fi
}

# comparar que un valor este en un conjunto
chequear_uno_de() { # $1=etiqueta  $2=obtenido  $3...=aceptados
  local etiqueta="$1" obtenido="$2"; shift 2
  local v
  for v in "$@"; do [ "$obtenido" = "$v" ] && { ok "$etiqueta: $obtenido"; return 0; }; done
  fallo "$etiqueta: se obtuvo '$obtenido' y se esperaba uno de: $*"
}

# linea final de cada script
resumen() {
  if [ "$FALLOS" -eq 0 ]; then ok "sin diferencias con lo verificado"
  else fallo "$FALLOS diferencia(s) con lo verificado. Corre 99-diagnostico.sh"; fi
}

# --- autenticacion ------------------------------------------------------------
CLAVE='DemoTFinder123!'

# token de una cuenta existente. Vacio si falla.
tok() { # $1=login|register  $2=json del cuerpo
  local r
  r=$(curl -s -X POST "localhost:8001/api/v1/auth/$1" -H 'Content-Type: application/json' -d "$2" \
      | jq -r '.access_token // ""')
  [ -n "$r" ] || printf '  no se pudo autenticar: %s\n' "$2" >&2
  printf '%s' "$r"
}

# token de una cuenta, creandola si todavia no existe. Idempotente.
alta() { # $1=email  $2=nombre
  local e="$1" n="$2" t
  # El primer intento se hace en silencio: si la cuenta no existe todavia, es lo
  # esperado, no un error. Solo se avisa si fallan los dos caminos.
  t=$(tok login "{\"email\":\"$e\",\"password\":\"$CLAVE\"}" 2>/dev/null)
  [ -n "$t" ] || t=$(tok register "{\"email\":\"$e\",\"password\":\"$CLAVE\",\"nombre\":\"$n\"}" 2>/dev/null)
  [ -n "$t" ] || printf '  no se pudo obtener el token de %s\n' "$e" >&2
  printf '%s' "$t"
}

# id de una cuenta, para no memorizar numeros
cuenta() { # $1=email
  docker compose exec -T postgres psql -U tfinder -d mesas_db -tAc \
    "select id||'  '||email from usuarios where email='$1'"
}

# contenido de un JWT, sin verificar la firma
decodificar() { # $1=token  -> imprime el payload
  local cabecera="${1%%.*}" resto="${1#*.}"
  local payload="${resto%%.*}"
  local relleno=$(( (4 - ${#payload} % 4) % 4 ))
  while [ "$relleno" -gt 0 ]; do payload="$payload="; relleno=$((relleno - 1)); done
  printf '%s' "$payload" | tr '_-' '/+' | base64 -d 2>/dev/null
}

# el campo jti de un token, para buscar la sesion en Redis
jti_de() { decodificar "$1" | jq -r '.jti // ""' 2>/dev/null
}

# --- peticiones ---------------------------------------------------------------

# peticion autenticada, devuelve el cuerpo
p() { # p TOKEN METODO URL [args extra de curl]
  local t="$1" m="$2" u="$3"; shift 3
  curl -s -X "$m" "$u" -H "Authorization: Bearer $t" "$@"
}

# peticion autenticada, devuelve solo el codigo HTTP
pc() { # pc TOKEN METODO URL [args extra de curl]
  local t="$1" m="$2" u="$3"; shift 3
  curl -s -o /dev/null -w '%{http_code}' -X "$m" "$u" -H "Authorization: Bearer $t" "$@"
}

# cuerpo y codigo en una sola llamada
pyc() { # pyc TOKEN METODO URL [args extra]
  local t="$1" m="$2" u="$3"; shift 3
  printf '%s [%s]\n' "$(p "$t" "$m" "$u" "$@")" \
    "$(pc "$t" "$m" "$u" "$@")"
}

# esperar a que un endpoint de salud responda el codigo pedido
esperar_ready() { # $1=url  $2=segundos maximo
  local u="$1" max="${2:-90}" i=0
  while [ "$i" -lt "$max" ]; do
    [ "$(curl -s -o /dev/null -w '%{http_code}' "$u")" = "200" ] && return 0
    i=$((i + 1)); sleep 1
  done
  return 1
}

# --- mesas de prueba ----------------------------------------------------------
# Los demos que necesitan vacantes no usan las mesas del seed, sino una propia.
# Asi el script se puede correr las veces que haga falta sin llenarlas.
#
# Imprime el id. Falla con codigo 1 si no se pudo crear.

mesa_de_prueba() { # $1=vacantes (default 6)  $2=prefijo del nombre
  local vacantes="${1:-6}" prefijo="${2:-Mesa Prueba}"
  local t nombre
  t=$(tok login "{\"email\":\"gm@tfinder.dev\",\"password\":\"$CLAVE\"}")
  [ -n "$t" ] || return 1
  nombre="$prefijo $(date +%H%M%S)"
  p "$t" POST localhost:8001/api/v1/mesas \
    -H 'Content-Type: application/json' \
    -d "{\"nombre\":\"$nombre\",\"sistema\":\"PF1e\",\"jugadores_max\":$vacantes}" \
    | jq -r '.id // empty'
}

# avisa si una mesa ya no tiene lugar, y que hacer al respecto
avisar_sin_vacantes() { # $1=mesa_id  $2=nombre de la mesa
  local id="$1" nombre="$2" estado
  estado=$(curl -s localhost:8001/api/v1/mesas/"$id" | jq -r '"\(.jugadores_actuales)/\(.jugadores_max)"')
  case "$estado" in
    *"/0") printf '  %s esta en 0/0: sin vacantes. Corre 00-reset.sh\n' "$nombre" >&2 ;;
  esac
  case "$estado" in
    *[!0-9/]*|"") printf '  no se pudo leer el estado de la %s\n' "$nombre" >&2; return 1 ;;
  esac
  local act="${estado%%/*}" max="${estado##*/}"
  if [ "$act" -ge "$max" ]; then
    printf '  la %s esta en %s: sin vacantes. Corre 00-reset.sh\n' "$nombre" "$estado" >&2
    return 1
  fi
  return 0
}
