#!/usr/bin/env bash
# Slide 11. Topologia de la mensajeria y el PDF asincrono de punta a punta.
#
# Uso:  bash scripts/demo/06-asincronia.sh
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

banner "SLIDE 11 - ASINCRONIA: TOPOLOGIA"

TOKEN=$(tok login "{\"email\":\"gm@tfinder.dev\",\"password\":\"$CLAVE\"}")

seccion "colas: mensajes pendientes y consumidores"
esperado "notif.mesa, notif.sesion y doc.pdf con 1 consumidor; dlq.general con 0"
docker compose exec -T rabbitmq rabbitmqctl list_queues -p / name durable messages_ready consumers 2>/dev/null \
  | grep -vE 'Timeout|Listing queues|^$'

seccion "bindings: el exchange hacia cada cola"
esperado "tfinder.events a tres colas de trabajo, y tfinder.dlx a la DLQ"
docker compose exec -T rabbitmq rabbitmqctl list_bindings -p / source_name destination_name routing_key 2>/dev/null \
  | grep -E '^tfinder'

nota "tres colas con un consumidor son tres hilos dentro de notif_api."
nota "La DLQ con cero es lo correcto: nadie la consume, la revisa una persona."


banner "SLIDE 11 - PDF ASINCRONO DE PUNTA A PUNTA"

# ------------------------------------------------------- 1. el turno se acepta --
seccion "1. builds_api acepta el turno y responde 202 de inmediato"
esperado "un documento_id nuevo en cada corrida"
DOC=$(p "$TOKEN" POST localhost:8002/api/v1/builds/1/pdf | jq -r '.documento_id // ""')
printf '  documento_id=%s\n' "$DOC"
[ -n "$DOC" ] && ok "el 202 trae el identificador" || fallo "el 202 no trajo documento_id"

# ------------------------------------------------- 2. el estado se va actualizando --
seccion "2. notif_api informa el estado hasta que deja de estar en proceso"
esperado "llega a \"estado\":\"listo\" en el primer o segundo intento"
listo=0
for i in $(seq 1 10); do
  ESTADO=$(p "$TOKEN" GET "localhost:8004/api/v1/pdf/$DOC/estado")
  printf '  [%s] %s\n' "$i" "$ESTADO"
  case "$ESTADO" in *'"listo"'*) listo=1; break;; esac
  sleep 1
done
[ "$listo" -eq 1 ] && ok "el documento llego a listo" || fallo "en 10 intentos nunca llego a listo"

# ------------------------------------------------------------- 3. la descarga --
seccion "3. descarga del archivo generado por el worker"
esperado "HTTP=200 type=application/pdf bytes=1257"
curl -s -o /tmp/tf-doc.pdf -w '  HTTP=%{http_code} type=%{content_type} bytes=%{size_download}\n' \
  "localhost:8004/api/v1/pdf/$DOC" -H "Authorization: Bearer $TOKEN"
file /tmp/tf-doc.pdf
chequear "tipo de contenido" \
  "$(curl -s -o /dev/null -w '%{content_type}' "localhost:8004/api/v1/pdf/$DOC" -H "Authorization: Bearer $TOKEN")" \
  "application/pdf"

seccion "el contrato: pedir el archivo antes de que este listo da 404 a proposito"
nota "no es un error del sistema, es el contrato: el cliente consulta el estado antes de descargar."

resumen
echo
echo "  Siguiente:  bash scripts/demo/07-seguridad.sh"
