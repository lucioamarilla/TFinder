## 1. Contrato REST de miembros (mesas-api)

- [x] 1.1 Modelo `listar_miembros(mesa_id)` (solicitudes aceptadas + usuarios) y endpoint `GET /api/v1/mesas/{mesa_id}/miembros` (auth)

## 2. Outbox e integración SMTP (notif-api)

- [x] 2.1 DDL tabla `emails` (outbox) en `notif_api/app/schema.sql`
- [x] 2.2 `models/notif.py`: `registrar_email`, `obtener_email`, `actualizar_estado_email`, `listar_emails`
- [x] 2.3 `services/email_service.py`: SMTP con timeout (3 s), outbox, token de servicio + `obtener_emails_mesa` por REST
- [x] 2.4 Consumer `sesion.py`: enviar emails en `sesion.confirmada` y `sesion.diario_publicado`
- [x] 2.5 Ruta `POST /api/v1/emails/{id}/reintentar`; env en docker-compose.yml

## 3. Verificación (done)

- [x] 3.1 `sesion.confirmada` → email en MailHog (API v2) + fila `emails` `enviado`
- [x] 3.2 `sesion.diario_publicado` → email del diario
- [x] 3.3 Fallo SMTP (puerto cerrado) → fila `fallido` con error, evento sigue procesado
- [x] 3.4 `POST /emails/{id}/reintentar` → pasa a `enviado`
- [x] 3.5 Replay del mismo `event_id` no duplica emails
- [x] 3.6 `openspec validate b09-proveedor-email`

## 4. Cierre de la tarea

- [ ] 4.1 Rama `f/B09_proveedor_email`, commit, merge y archivar
- [ ] 4.2 Cerrar issue GitHub #22