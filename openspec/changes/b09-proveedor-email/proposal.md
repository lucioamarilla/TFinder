# Proposal: Integración externa con proveedor de email (MailHog)

## Why

Criterio AE2 9 (evidencia) y 5 (integración con manejo de fallos): confirmar una sesión o publicar su diario debe notificar por email a los jugadores de la mesa, usando un proveedor SMTP en sandbox (MailHog, ya presente desde B01). El envío es controlado: timeout de 3 s, outbox de fallidos con retry, y no rompe el flujo si el SMTP cae.

## What Changes

- **`notif_db`**: tabla `emails` (outbox: destino, asunto, cuerpo, estado `enviado|fallido`, error, fecha).
- **`notif-api`**: `services/email_service.py` (`smtplib` con `socket.timeout`; `MIMEText` HTML/texto simple; `MAIL_FROM`; timeout por env `SMTP_TIMEOUT=3`). Extiende el consumidor `sesion.py` (B05): en `sesion.confirmada` y `sesion.diario_publicado` obtiene los destinos por el **contrato REST de mesas-api** (`GET /api/v1/mesas/{id}/miembros`) — no SQL a mesas_db (interoperabilidad correcta). Endpoint `POST /api/v1/emails/{id}/reintentar` para el retry del outbox.
- **`mesas-api`**: endpoint `GET /api/v1/mesas/{mesa_id}/miembros` (auth) lista los jugadores aceptados (solicitudes_uniones + usuarios) con `email`, `nombre`, `id`.
- **Compose**: env para notif (`SMTP_HOST=mailhog`, `SMTP_PORT=1025`, `MAIL_FROM`, `MESAS_URL=http://mesas-api:8001`, credenciales de servicio).
- **Privacidad**: el email usa asunto/cuerpo genéricos (sin datos sensibles) y solo llega a los jugadores de la mesa.

## Capabilities

- **New Capabilities**: `proveedor-email` — envío SMTP con timeout y outbox de fallidos con reintento; contrato REST de miembros de mesa.
- **Modified Capabilities**: `eventos-rabbitmq` — el consumidor `sesion.*` ahora además envía emails; `concurrencia-vacantes` — sin cambios (el endpoint de miembros lee `solicitudes_uniones` estado `aceptada`).

## Impact

- `mesas-api`: 1 endpoint nuevo (rutas+modelo), sin cambios en DDL.
- `notif-api`: tabla nueva en `notif_db`, worker `sesion` extendido, 1 ruta nueva, dependencia HTTP a mesas-api (network interna) y a MailHog.
- Evidencia para portafolio: bandeja de MailHog (http://localhost:8025).