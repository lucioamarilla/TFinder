# Design: Integración externa con proveedor de email (MailHog)

## Context

B05 dejó el consumidor `sesion.*` (notificación en BD) y B08 el patrón worker. Ahora se agrega un proveedor SMTP externo (MailHog, ya en compose desde B01). La regla AE2: `notif-api` NO toca `mesas_db`; obtiene destinatarios por REST de mesas-api (criterio 8: interoperabilidad por contrato).

## Decisions

**D1 — Destinos por contrato REST de mesas-api.**
Nuevo `GET /api/v1/mesas/{mesa_id}/miembros` (auth) en mesas-api: `SELECT u.id, u.nombre, u.email FROM usuarios u JOIN solicitudes_uniones s ON s.usuario_id = u.id WHERE s.mesa_id=%s AND s.estado='aceptada'`. `notif-api` lo consulta con un access token de un usuario de servicio (login en mesas-api con `MESAS_EMAIL`/`MESAS_PASSWORD`), cacheado en memoria. Nunca SQL a mesas_db.

**D2 — `smtplib` con timeout y sin dependencias nuevas.**
`email_service.py`: `smtplib.SMTP(host, port, timeout=SMTP_TIMEOUT|3)`. Se usa `urllib.request` (stdlib, timeout 3) para el REST, evitando agregar `requests`.

**D3 — Outbox en `notif_db` con reintento.**
Tabla `emails` (destino, asunto, cuerpo, estado `enviado|fallido`, error, fecha). `enviar_email()` nunca lanza por SMTP: registra `fallido` y devuelve `False` (el consumidor hace ACK igual; no se pierde). El reintento manual `POST /api/v1/emails/{id}/reintentar` reusa asunto/cuerpo/destino guardados y actualiza el estado.

**D4 — Consumer `sesion.*` extendido (B05 + email).**
En `_procesar`: (1) idempotencia por `event_id`; (2) guardar_notificación (ya existente); (3) obtener miembros por REST y enviar email a cada uno. Si el REST a mesas falla (mesas-api caído), se propaga la excepción → reintentos backoff → DLQ (no se pierde el evento). Si solo el SMTP falla, NO se propaga (outbox lo retiene).

**D5 — Config por env (compose).**
`notif-api`: `SMTP_HOST=mailhog`, `SMTP_PORT=1025`, `MAIL_FROM=noreply@tfinder.local`, `SMTP_TIMEOUT=3`, `MESAS_URL=http://mesas-api:8001`, `MESAS_EMAIL`, `MESAS_PASSWORD`. Sin cambios en la imagen (solo env).

**D6 — Contenido mínimo y privado.**
Asuntos genéricos por tipo; cuerpo plano MIMEText utf-8 ("Tu grupo confirma la próxima sesión de la mesa {id}. ¡Nos vemos!"). Sin secretos ni datos personales.

## Risks

- **Credencial MESAS_PASSWORD en env del compose**: cuenta de servicio de desarrollo creada en la verificación; documentada (mismo criterio que tfinder/tfinder).
- **Token cacheado sin expiración explícita**: si mesas responde 401, en el reintento del worker se vuelve a loguear (se limpia la caché ante 401).
- **MailHog sin healthcheck**: el worker reintenta conexión cada 3 s si SMTP cae; no bloquea el ACK.

## Migration Plan

1. `mesas_api`: `listar_miembros` en modelo de sesiones + endpoint `GET /mesas/{id}/miembros` (auth).
2. `notif_api`: DDL `emails`; modelo `registrar_email`, `obtener_email`, `listar_emails`, `actualizar_estado_email`.
3. `notif_api`: `services/email_service.py` (SMTP + REST mesas + token service).
4. `notif_api`: consumer `sesion.py` extendido + ruta `POST /api/v1/emails/{id}/reintentar`; compose env.
5. Verificación: disparar eventos, revisar MailHog y `emails`; simular fallo (SMTP_PORT cerrado) y reintento.
6. Rama, commit, merge, archivar, cerrar #22.

## Verification

- Publicar `sesion.confirmada` (mesa con jugadora aceptada) → email en MailHog (API v2) + fila `enviado`.
- Publicar `sesion.diario_publicado` → email del diario.
- `SMTP_PORT=9` en un one-off → `enviar_email` devuelve False y la fila queda `fallido` con error.
- `POST /api/v1/emails/{id}/reintentar` → `enviado`.
- Un evento repetido (mismo `event_id`) no duplica emails (idempotencia).
- `openspec validate b09-proveedor-email`.