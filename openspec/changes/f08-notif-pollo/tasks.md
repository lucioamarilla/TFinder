## 1. Implementación

> Nota: la implementación original de esta tarea (`1b13721`) fue revertida en `efd95d6`, así que los `[x]` previos no describían el estado real del repo. La lista de abajo es la que quedó después de reimplementar F08.

- [x] 1.1 Backend (ya estaba, `5d4a635`): `PATCH /notificaciones/{id}/leida` + `creado_en` en `NotificacionOut` + `enlace` como `{label, to}`
- [x] 1.2 `endpoints.js`: reutiliza `notifApi` existente (notificaciones + marcarLeida), sin cambios
- [x] 1.3 `services/notificaciones.js`: `normalizarNotificacion` + `formatearFecha`; `fecha` sale de `creado_en` (la columna `fecha` de la tabla nunca se escribe) y `enlace` se normaliza a `{label, to}`, descartando el que no traiga `to`
- [x] 1.4 `services/notificaciones.js`: se elimina `getNoLeidas()`; el contador se deriva de la lista en memoria
- [x] 1.5 `useNotifications.js`: `lista`, `unreadCount`, `desconectado` y `ultimoError` pasan a estado compartido de módulo; una sola llamada a `getNotificaciones()` por tick de 5 s
- [x] 1.6 `useNotifications.js`: `loadCount` se renombra a `refrescar` y `setUnread` se borra (sin usos)
- [x] 1.7 `AppHeader.vue`: badge real + campana en gris con `sim-bell-off`, sin cambios (ya consumía `unreadCount`/`desconectado`)
- [x] 1.8 `NotificacionesView.vue`: usa la lista compartida, botón "Recargar", banner offline y navegación por `enlace.to`
- [x] 1.9 `NotificacionesView.vue`: se borra el botón mock "Cargar Notificaciones Anteriores"
- [x] 1.10 `DashboardView.vue`: call site actualizado a `refrescar()`
- [x] 1.11 Tests: `tests/unit/notificaciones.spec.js` (13) y `tests/unit/useNotifications.spec.js` (13)
- [x] 1.12 `npm run lint` y `npm run build` sin errores

## 2. Verificación

- [x] 2.1 `npm test` → 63/63 (37 previos + 26 nuevos)
- [x] 2.2 El polling pide una sola vez por tick y el contador se deriva de la lista compartida
- [x] 2.3 `notif-api` caído → `desconectado=true`, contador en 0, la lista conocida se conserva y la app sigue navegable
- [x] 2.4 `notif-api` restaurado → el siguiente tick repuebla badge y lista
- [ ] 2.5 Flujo end-to-end con `mesas-api` + `notif-api` arriba: solicitud de unión → notificación por RabbitMQ visible sin refresh. **Pendiente de verificación manual** (el catálogo de `services/builds.js` sigue mock; requiere sesión y servicios levantados)
- [x] 2.6 `openspec validate f08-notif-pollo` — no se puede ejecutar: el CLI de `openspec` no está instalado en la máquina

## 3. Cierre de la tarea

- [ ] 3.1 Commit en `f/F07_pdf_async` (la entrega de F08 se apila sobre F07, un solo PR al final)
- [ ] 3.2 Push, pull y PR quedan para el final del proyecto, por decisión del usuario
- [ ] 3.3 Cerrar issue GitHub #33
