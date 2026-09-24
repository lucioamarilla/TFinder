# Proposal: Notificaciones en vivo desde notif-api (eventos RabbitMQ)

## Why

La campana del `AppHeader` y `NotificacionesView` leían un JSON mock. Ahora consumen lo que `notif-api` persiste (alimentado por eventos RabbitMQ): solicitudes de unión, sesiones, updates de mesa. Al disparar una acción en `mesas-api` (ej. solicitar unirse), en ~2-5 s aparece la notificación vía polling (5 s) sin refresh manual. Si `notif-api` cae, la app no se rompe: badge gris y aviso "sin conexión a avisos".

## What Changed

- **`src/services/notificaciones.js`**: mock reemplazado por llamadas reales a `notifApi` (mismas exportaciones). `enlace` llega como dict `{"/mesas/N": "ver mesa"}` y se mapea a `{label, to}`; `fecha` se formatea de `creado_en` a `es-CO`.
- **`src/composables/useNotifications.js`**: estado compartido de módulo (`lista`, `noLeidas`, `desconectado`) con polling cada 5 s; el `catch` pone `desconectado=true` sin romper la app.
- **`src/components/AppHeader.vue`**: badge = `noLeidas` real (se oculta en offline), campana en gris y aviso "sin conexión a avisos".
- **`src/views/NotificacionesView.vue`**: usa `lista` compartida + botón "Recargar" + aviso offline; `abrir()` navega con `enlace.to` real; marcar leída/todas refresca el badge.
- **Backend `notif-api`** (aditivo): endpoint `PATCH /api/v1/notificaciones/{id}/leida` (antes no existía) y `creado_en` en `NotificacionOut`.

## Impact

- Flujo verificado: solicitar unirse a mesa con vacante → 201 → en 4 s la notificación "Solicitud aceptada" con `enlace /mesas/3` persiste y aparece para el polling (total 38→39).
- Offline: `docker stop` → la llamada no responde → `desconectado=true`; app sigue; `docker start` → vuelve a autopoblar.
- `src/data/notificaciones.json` deja de usarse en el camino feliz.