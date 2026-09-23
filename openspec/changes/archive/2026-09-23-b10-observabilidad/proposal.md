# Proposal: Observabilidad base — logs JSON con correlation_id, /live y /ready

## Why

Dejar evidencia operacional distribuida (RNF-13/RNF-16): los 4 servicios deben emitir logs **estructurados en JSON** con un `correlation_id` que atraviese un recorrido completo, y exponer `/live` (proceso vivo) y `/ready` (dependencias OK) para el admin de F09.

## What Changes

- **Logger JSON compartido** en `app/infra/logge.py` (raíz, imagen única, mis- mos patrones de `redis.py`/`rabbitmq.py`): `ts`, `nivel`, `servicio`, `mensaje`, `correlation_id` (default `-`) y `exc` opcional.
- **Contexto de correlación**: `ContextVar` en el módulo de logge + `log_record_factory` — todo log emitido dentro de un request lleva el CID sin tocar cada call-site.
- **Middleware ASGI compartido** `app/middleware/log_context.py`: lee `X-Correlation-Id` (o genera uno), lo pone en el `ContextVar`, registra entrada/salida del request con ese CID y lo devuelve en el header de respuesta.
- **Propagación a eventos**: `publicar()` en `app/infra/rabbitmq.py` inyecta `correlation_id` en el payload (tomándolo del `ContextVar`); el consumidor lo usa como CID en B05. Grep de un CID en `event-log` de notif cuando ya exista el pipeline de eventos.
- **`/live` y `/ready`** en los 4 servicios: `/ready` chequea PostgreSQL (pool propio), Redis (`get_redis().ping()`) y RabbitMQ (conexión `pika`); si alguna falla → `503` con el detalle de dependencias.

## Capabilities

- **New Capabilities**: `observabilidad` — logs JSON + correlación + reputación de salud en los 4 servicios.
- **Modified Capabilities**: ninguna.

## Impact

- Ruptura de contrato de logs: la salida pasa de texto a JSON (no rompe API, sí cambia el formato de consola del operador).
- No se imprimen tokens, contraseñas ni QRs completos (RNF-23 básico): B05/consumer loggearán solo metadatos.
- `/ready` agrega 3 conexiones salientes por chequeo (Postgres/Redis/RabbitMQ); barato y bajo demanda.