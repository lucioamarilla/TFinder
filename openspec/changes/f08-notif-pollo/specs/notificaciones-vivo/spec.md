# Purpose

Conectar la campana de notificaciones del frontend a `notif-api` real (persistencia alimentada por eventos RabbitMQ), con polling cada 5 s, badge de no leídas, marcar leída/todas, navegación por enlace real a la ruta del front y manejo degradado cuando `notif-api` está caído.

## ADDED Requirements

### Requirement: Consumo en vivo de notificaciones reales
El `AppHeader` y `NotificacionesView` DEBEN dejar de leer el JSON mock y consumir `GET /api/v1/notificaciones` de `notif-api`. El badge DEBE mostrar el total de no leídas y actualizarse por polling cada ~5 s sin refresh manual. El polling DEBE resolver la lista con una sola llamada por tick y derivar de ella el contador de no leídas, de modo que la lista abierta y el badge no puedan desincronizarse.

#### Scenario: Aparece una notificación sin recargar
- **GIVEN** el usuario logueado con el polling activo
- **WHEN** dispara una solicitud de unión a una mesa con vacante (F04)
- **THEN** en ~2-5 s el badge muestra +1 y `NotificacionesView` lista la notificación persistida por `notif-api`, con fecha formateada `es-CO`
- **AND** la fecha mostrada se deriva de `creado_en`, porque la columna `fecha` de la tabla no la escribe ningún productor

### Requirement: Marcar leída y marcar todas
`PATCH /api/v1/notificaciones/{id}/leida` DEBE marcarla y el badge DEBE decrementar. "Marcar todas como leídas" DEBE iterar las no leídas y refrescar el conteo.

#### Scenario: El badge baja al marcar
- **GIVEN** un aviso sin leer con badge `N`
- **WHEN** el usuario abre la notificación o usa "Marcar todas"
- **THEN** el badge queda `N-1` (o `0`) y el item sale con estilo de leído

### Requirement: Enlace navega a la ruta real
`notif-api` entrega `enlace` como `{label, to}` donde `to` ya es una ruta del front, y `abrir()` DEBE navegar con `router.push(enlace.to)`. El front NO DEBE inventar la ruta a partir de la entidad ni traducir un dict `{"/mesas/N": "ver mesa"}`: un `enlace` sin `to` se descarta y el aviso se muestra sin enlace.

### Requirement: Degradación offline
Si `notif-api` está caído, el front MUST NOT romperse: badge en gris (sin número), aviso discreto "sin conexión a avisos" y al restaurar el servicio el polling DEBE volver a autopoblar. La última lista conocida DEBE conservarse en vez de vaciarse, para que el usuario no vea la bandeja en blanco.

#### Scenario: notif-api caído
- **GIVEN** `notif-api` detenido
- **WHEN** el polling intenta refrescar y falla la conexión
- **THEN** `desconectado=true`, el contador queda en 0, se muestra el aviso y la app sigue navegable
- **AND** al iniciar `notif-api`, el siguiente refresco restaura el badge y la lista