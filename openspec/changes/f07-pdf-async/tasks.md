## 1. Implementación

- [x] 1.1 `endpoints.js`: `pdfApi.solicitarBuild` (202) y `pdfApi.estado` (404/200)
- [x] 1.2 `usePdfDescarga.js`: máquina de estados + polling 2 s + descarga real
- [x] 1.3 `BuildDetailView.vue`: botón "Exportar PDF" con 4 estados y badge async
- [x] 1.4 `BuildHistorialView.vue`: mismo patrón (reemplaza mock `exportarHistorial`)
- [x] 1.5 `npm run build` compila sin errores

## 2. Verificación

- [x] 2.1 `POST /builds/1/pdf` con token real → `202 {estado:'aceptado', documento_id}`
- [x] 2.2 `GET /pdf/{doc}` → 404 en proceso, luego 200 `application/pdf` (1263 bytes, PDF 1 página)
- [x] 2.3 `openspec validate f07-pdf-async`

## 3. Cierre de la tarea

- [ ] 3.1 Rama `f/F07_pdf_async`, commit, merge y archivar
- [ ] 3.2 Cerrar issue GitHub #32