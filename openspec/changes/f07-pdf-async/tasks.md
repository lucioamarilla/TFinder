## 1. Implementación

> Reimplementada sobre `origin/AE2-Testing` (`7b74bd0`) en la rama `f/F07_pdf_async`. La
> versión anterior de estas tareas (`2c57f14`) fue revertida por `efd95d6` ("tareas pasan a
> backend") y el código frontend quedó ausente del árbol, pero los checkboxes nunca se
> desmarcaron. La implementación de abajo corrige dos defectos de aquella versión: la
> descarga usaba `window.open` sin cabecera `Authorization` (401 garantizado) y el estado se
> deducía de la diferencia entre 404 y 200 en lugar de consultar `/pdf/{id}/estado`.

- [x] 1.1 `endpoints.js`: `pdfApi.solicitarBuild` (202 a builds-api), `pdfApi.estado` contra `GET /api/v1/pdf/{id}/estado` (200 con `estado ∈ {en_proceso, listo, error}` / 404) y `pdfApi.descargar` vía `apiBlob`
- [x] 1.2 `usePdfDescarga.js`: máquina de estados (`inactivo|enviando|en_cola|descargando|listo|error|cancelado`), polling 2 s encadenado con `setTimeout` (sin solapamiento de consultas), techo de 30 intentos y descarga por blob con `URL.createObjectURL`
- [x] 1.3 `BuildDetailView.vue`: botón "Exportar PDF" con 4 estados visibles, botón "Cancelar" durante la cola y toast al quedar listo o al fallar
- [x] 1.4 `BuildHistorialView.vue`: mismo patrón vía `usePdfDescarga(solicitar, 'Exportar historial')`; elimina el mock `exportarHistorial` de `services/builds.js`
- [x] 1.5 `npm run lint`, `npm test` (37/37) y `npm run build` compilan sin errores
- [x] 1.6 `config/features.js`: `builds` y `admin` habilitadas para que las rutas `/builds/*` y `/admin/*` dejen de redirigir a `ComingSoonView`

## 2. Verificación

- [x] 2.1 `POST /builds/1/pdf` con token real → `202 {estado:'aceptado', documento_id}`
- [x] 2.2 `GET /pdf/{doc}` → 404 en proceso, luego 200 `application/pdf` (1263 bytes, PDF 1 página)
- [x] 2.3 `openspec validate f07-pdf-async`

## 3. Cierre de la tarea

- [ ] 3.1 Rama `f/F07_pdf_async`, commit, merge y archivar
- [ ] 3.2 Cerrar issue GitHub #32