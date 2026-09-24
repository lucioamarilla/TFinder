# Purpose

Conectar el listado y detalle de mesas del frontend con `mesas-api` (`/api/v1/mesas`), consumiendo la caché Redis del backend y dejando evidencia visible del comportamiento cache-aside (1ª carga vs 2ª carga), con estados de error y reintento cuando el servicio está caído.

## ADDED Requirements

### Requirement: Servicio de mesas real
`src/services/mesas.js` DEBE implementar `getMesas`/`getMesa`/`crearMesa`/`actualizarMesa`/`eliminarMesa` sobre `mesasApi`, conservando la firma y los nombres de campo internos que usan las vistas, y DEBE normalizar el contrato real del backend (`jugadores_actuales`, `jugadores_max`, `nivel_inicial`, `estado`) al shape interno sin leer `src/data/mesas.json`.
`getMesas` DEBE medir el tiempo de respuesta con `performance.now()` y exponerlo vía `ultimaMedicion()`.

#### Scenario: Listado desde la API
- **WHEN** la vista carga la lista de mesas
- **THEN** los datos provienen de `GET /api/v1/mesas` (caché Redis del backend) y no del catálogo mock

### Requirement: Evidencia de caché visible
`MesasListView` DEBE mostrar la medición de la última carga (chip "caché ~X ms") y permitir recargar para comparar 1ª carga (DB+Redis) vs cargas siguientes (caché).

#### Scenario: Refrescar mide de nuevo
- **WHEN** el usuario presiona "Refrescar"
- **THEN** se vuelve a llamar al API, se actualiza el listado y el chip muestra la nueva latencia

### Requirement: Detalle real con campos del contrato
`MesaDetailView` DEBE renderizar los campos reales del API `{id, nombre, sistema, descripcion, jugadores (jugadores_actuales), plazas (jugadores_max), nivel inicial, estado}` y contar con reintento cuando la carga falla.

#### Scenario: Servicio caído
- **WHEN** `mesas-api` no responde
- **THEN** se muestra el estado de error y un botón "Reintentar" que relanza la carga (sin pantalla en blanco)