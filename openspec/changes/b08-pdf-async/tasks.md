## 1. Almacenamiento y generación (notif-api)

- [x] 1.1 `notif_api/app/schema.sql`: tabla `documentos`
- [x] 1.2 `notif_api/app/models/notif.py`: `crear_documento`, `actualizar_documento`, `obtener_documento`
- [x] 1.3 `notif_api/app/services/pdf_service.py`: `generar_pdf_build`, `generar_pdf_diario` (fpdf2, PDF_DIR)
- [x] 1.4 `notif_api/app/workers/pdf.py`: consume `doc.pdf.*` (idempotencia + DLQ) y registra en main

## 2. Pedido síncrono (builds-api)

- [x] 2.1 `builds_api/app/middleware/auth.py` (patrón B03) y registro en main
- [x] 2.2 `builds_api/app/services/eventos.py`: `publicar_doc_pdf` (doc_id uuid + datos del build)
- [x] 2.3 `builds_api/app/routes/v1/build_pdf.py`: `POST /builds/{id}/pdf` → `202` con documento_id

## 3. Verificación (done)

- [x] 3.1 `POST /builds/{id}/pdf` → `202` en <300ms con `documento_id`
- [x] 3.2 Tras unos segundos `GET /api/v1/pdf/{doc}` → `200` `application/pdf`; `file` confirma
- [x] 3.3 PDF contiene datos del build (persona/clase/nivel) y sin datos sensibles
- [x] 3.4 Fila `documentos` en `listo`; DLQ no contiene el evento
- [x] 3.5 `openspec validate b08-pdf-async`

## 4. Cierre de la tarea

- [ ] 4.1 Rama `f/B08_pdf_async`, commit, merge y archivar
- [ ] 4.2 Cerrar issue GitHub #21