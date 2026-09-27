# Proposal: Notificaciones en vivo desde notif-api (eventos RabbitMQ)

## Why

La campana del `AppHeader` y `NotificacionesView` leían un JSON mock. Ahora consumen lo que `notif-api` persiste (alimentado por eventos RabbitMQ): solicitudes de unión, sesiones, updates de mesa. Al disparar una acción en `mesas-api` (ej. solicitar unirse), en ~2-5 s aparece la notificación vía polling (5 s) sin refresh manual. Si `notif-api` cae, la app no se rompe: badge gris y aviso "sin conexión a avisos".

## What Changed

- **`src/services/notificaciones.js`**: mock reemplazado por llamadas reales a `notifApi` (mismas exportaciones). Se agrega `normalizarNotificacion`: `fecha` sale de `creado_en` porque la columna `fecha` de la tabla nunca se escribe, formateada a `es-CO` (si el valor no parsea, se muestra tal cual); `enlace` llega de `notif-api` como `{label, to}` y se pasa tal cual, descartando el que no traiga `to`. Se elimina `getNoLeidas()`: el contador se deriva de la lista.
- **`src/composables/useNotifications.js`**: estado compartido de módulo (`lista`, `unreadCount`, `desconectado`, `ultimoError`) con polling cada 5 s y **una sola** llamada a `getNotificaciones()` por tick; el `catch` marca `desconectado`, pone el contador en 0 y conserva la última lista conocida sin romper la app.
- **`src/components/AppHeader.vue`**: badge = `unreadCount` real (se oculta cuando es 0, incluso offline) y campana en gris con `sim-bell-off`. Sin cambios: ya consumía el composable.
- **`src/views/NotificacionesView.vue`**: usa la lista compartida + botón "Recargar" + banner offline; `abrir()` navega con `enlace.to` real; marcar leída/todas refresca el estado compartido.
- **Backend `notif-api`** (ya aplicado en `5d4a635`): endpoint `PATCH /api/v1/notificaciones/{id}/leida`, `creado_en` en `NotificacionOut` y `enlace` como `{label, to}`.

## Impact

- Requests por tick: de 2 a 1 (se eliminó el `?solo_no_leidas=true` en cada tick).
- Offline: `docker stop` → la llamada falla → `desconectado=true`, contador en 0, campana en gris, banner con la última lista conocida; `docker start` → el siguiente tick restaura badge y lista.
- `src/data/notificaciones.json` deja de usarse en el camino feliz.
- Tests: 63/63 con `npm test` (26 nuevos), `npm run lint` y `npm run build` limpios.
- **Pendiente de backend (no se toca en esta tarea):** `guardar_notificacion()` nunca escribe `grupo`, `icono` ni `autor`, así que la DB aplica sus defaults (`grupo='mesas'`, `icono='solicitud'`, `autor=NULL`). Consecuencia visible: 2 de las 4 pestañas de filtro quedan siempre en 0 y 5 de los 6 iconos nunca se pintan. Se documenta en vez de inventar reglas de negocio en el front.