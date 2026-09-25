# Proposal: Explorar mesas reales contra `mesas-api`

## Why

`MesasListView`/`MesaDetailView` giraban sobre el mock de `src/data/mesas.json`. F03 los migra al endpoint real `/api/v1/mesas` (B02/B04), consumiendo la caché Redis del backend y dejando evidencia en la propia UI del comportamiento cache-aside (tiempo de 1ª vs 2ª carga).

## What Changes

- **`src/services/mesas.js`**: reimplementado sobre `mesasApi` (listar/detalle/crear/actualizar/eliminar) conservando la firma y los nombres de campo internos que usan las vistas; normaliza el contrato real `{jugadores_actuales, jugadores_max, nivel_inicial, estado, ...}` al shape de las vistas (`jugadores/plazas/rangoNivel/estado/estadoCategoria/vacante`) con valores por defecto para los campos que el API no expone. Mide con `performance.now()` y expone `ultimaMedicion()`.
- **`src/api/endpoints.js`**: `actualizar`/`eliminar` en `mesasApi`; `solicitarUnion` apunta a la ruta real `/mesas/{id}/solicitar`.
- **`MesasListView.vue`**: chip "caché ~X ms" con la medición de cada carga + botón "Refrescar"; el error (servicio caído) sigue con "Reintentar".
- **`MesaDetailView.vue`**: campos reales del API (nombre, sistema, descripción, jugadores/plazas, nivel inicial, estado) y botón "Reintentar" en el estado de error.

## Capabilities

- **New Capabilities**: `explorar-mesas-real` — listado/detalle reales con medición visible de caché y estados de error/retry.

## Impact

- `src/data/mesas.json` queda como dato histórico (fallback documentado), fuera del camino feliz. Otras vistas que importan `src/services/mesas.js` conservan su API.