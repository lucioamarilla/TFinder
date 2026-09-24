# Proposal: Backend pendiente de #32 · #33 · #34 (PDF diario, estado de documento, SSE de notificaciones, tests/evidencias de admin)

## Why

El backend base de los tres frontends ya existe (B08/B10/B05): PDF de ficha 202, `/live`+`/ready`, DLQ, event-log. Al revisar como tareas de backend quedaron tres huecos funcionales reales, más la capa de tests/evidencias que exige la consigna AE2:

1. **#32**: nadie publica `doc.pdf.diario`; `feed-api` no tiene endpoint de diario; `documentos.estado` nunca pasa a `error`; falta `GET /pdf/{id}/estado`.
2. **#33**: la entrega "en vivo" es solo polling del cliente — no existe emisión server-sent events desde `notif-api`.
3. **#34**: la capa admin se verificó por curl pero no tiene tests automatizados ni evidencias en `AE2/evidencias`.

## What Changed

- **`feed_api`** (nuevo): `services/eventos.py` (`publicar_diario_pdf`) + `routes/v1/diario.py` con `POST /api/v1/mesas/{mesa_id}/sesiones/{sesion_id}/diario/pdf` → 202, protegido con **auth JWT** (middleware `app.middleware.auth` compartido / decodificación con `JWT_SECRET` + sesión en Redis). Datos del diario armados desde `wiki_paginas` de la mesa.
- **`notif_api`**:
  - `models/notif.py`: `marcar_documento_error(doc_id)` y helper de serialización para el estado.
  - `routes/v1/pdf.py`: `GET /pdf/{documento_id}/estado`.
  - `workers/pdf.py`: en fallo, marcar `estado='error'` antes de reencolar/DLQ.
  - `services/stream.py` (nuevo, `StreamHub` en memoria) + `routes/v1/notificaciones.py`: `GET /notificaciones/stream` (SSE).
  - `consumers/mesa.py`, `consumers/sesion.py`: publican en el hub tras `guardar_notificacion`.
- **`tests/`**: `test_dlq_operativo.py`, `test_ready_degradado.py`, `test_event_log_correlation.py`.
- **`AE2/evidencias/`**: nuevas capturas + `EVIDENCIAS.md` actualizado.

## Impact

- El flujo de diario PDF queda end-to-end: 202 → estado `listo` → `application/pdf` real; ante fallo, `estado='error'` consultable.
- Notificaciones en vivo por SSE con polling intacto.
- Capa admin con tests y evidencias reproducibles.
- Sin cambios de esquema disruptivos: todo aditivo (solo hay que **rebuild** de `feed-api`/`notif-api` por código nuevo).