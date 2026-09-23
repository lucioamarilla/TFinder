# ADR-005 · Integración externa sandbox: MailHog con timeout y outbox

- Estado: **Aceptado**
- Fecha: 2026-09-23

## Contexto

notif-api debe enviar correos de "Sesión confirmada" y "Diario de sesión publicado" a los miembros de una mesa. No se disponía de un proveedor SMTP externo real, y la entrega de email es una operación lenta y frágil que no debe bloquear el consumo de eventos de RabbitMQ (B09).

## Decisión

- **MailHog v1.0.1 como SMTP sandbox** en compose: captura los correos sin enviarlos a internet, con UI en `8025` y API en `http://localhost:8025/api/v2/messages`.
- **`SMTP_TIMEOUT = 3`** en el cliente `smtplib`: un proveedor lento/caído no cuelga el worker.
- **Outbox en notif_db (tabla `emails`)**: cada correo se registra con `estado enviado|fallido`, `error` y `fecha`; `enviar_email` envuelve el SMTP en try/except y **nunca lanza** — el evento fue procesado (ACK) y el fallo queda visible para reintento manual vía `POST /api/v1/emails/{id}/reintentar`.
- **Destinos por contrato REST**: notif-api obtiene los miembros con una cuenta de servicio (`email_svc@tfinder.dev`), vía `GET /api/v1/mesas/{id}/miembros` de mesas-api, con token cacheador.

## Consecuencias

- **Positivas**: desarrollo sin infraestructura externa ni envíos reales; fallos de SMTP no pierden eventos (ACK + registro `fallido`); reintento individual sin re-procesar el evento; timeout corto protege al worker.
- **Negativas**: MailHog es in-memory (al reiniciar el contenedor pierde la bandeja, aunque el outbox persiste); en producción habría que reemplazar el transporte por un proveedor real manteniendo el patrón outbox; la lógica de `_llamar_mesas` (urllib) duplica el cliente HTTP del resto del stack.