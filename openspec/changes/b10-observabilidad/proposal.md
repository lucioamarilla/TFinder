# Proposal: Observabilidad base (logs JSON, correlation_id, /live y /ready)

## Why

Criterios AE2 13/RNF-16: dejar evidencia operacional distribuida. Todos los servicios deben loguear en JSON con `correlation_id` (travesía request → evento → consumidor), propagarlo vía header `X-Correlation-Id` y exponer `/live` y `/ready` con chequeo real de dependencias. La infraestructura base ya existe desde B02/B05 (`app/infra/logge.py`, `app/middleware/log_context.py`, `app/infra/ready.py`, `/live` en los 4 mains): este change formaliza la capacidad con spec explícita y la verifica punta a punta.

## What Changes

- **Documentación/formalización** (código ya existente desde B02/B05): `app/infra/logge.py` (JsonFormatter: `ts, nivel, servicio, mensaje, correlation_id`, fallback ContextVar), `app/middleware/log_context.py` (lee `X-Correlation-Id`, setea ContextVar → lo propaga a `publicar()`, reenvía el header en la respuesta), `app/infra/ready.py` (postgres+redis+rabbitmq), `/live` y `/ready` en mesas/builds/feed/notif-api.
- **Ajustes de validación** si la verificación los pide (p. ej. /ready 503 con postgres caído).
- **Evidencia del recorrido**: request con `X-Correlation-Id` → `POST /mesas/{id}/solicitar` publica `mesa.solicitada` → consumidor notif loguea "evento procesado" con el mismo CID (≥3 logs en 2 servicios).

## Capabilities

- **New Capabilities**: `observabilidad` — logs JSON con correlación distribuida y endpoints de salud (`/live`, `/ready`).
- **Modified Capabilities**: `eventos-rabbitmq` — los mensajes ya llevan el `correlation_id` del request (confirmado por esta spec).

## Impact

- Ninguno estructural: la infra ya está compartida en `app/` y usada por los 4 servicios. Verificación + evidencias para el Portafolio (F09 podrá consultar `/ready`).