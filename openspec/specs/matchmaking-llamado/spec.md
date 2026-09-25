# Purpose

Conectar `MatchmakingView` con las mecánicas reales de "llamado abierto": el GM abre el llamado contra `mesas-api` (TTL de Redis de 120 s), el frontend muestra el `ttl_restante` real vía polling, y la expiración cierra el llamado sin depender del timer del navegador. Los jugadores se anotan con la solicitud idempotente de B06/F04, cuyo resultado real (201/409) se muestra en la tarjeta.

## Requirements

### Requirement: Abrir llamado con autoridad de expiración en Redis
`MatchmakingView` DEBE permitir a un usuario con rol `gm` abrir el llamado de una mesa con vacante vía `matchmakingApi.abrir`. El chip del llamado DEBE mostrar el estado y el `ttl_restante` que devuelve `matchmakingApi.estado` (polling de 2 s), tomado del TTL real en Redis de `mesas-api`, no de un countdown local.

#### Scenario: Cuenta regresiva en vivo desde Redis
- **GIVEN** el GM abrió el llamado de una mesa
- **WHEN** el frontend consulta `estado` cada 2 s
- **THEN** el chip muestra `estado: abierto · N s` con `N` igual al `ttl_restante` del backend, decreciendo hasta `cerrado` (ttl 0) cuando expira en Redis
- **AND** al recargar la página, el llamado sigue su TTL real (abierto y decreciente, o cerrado si expiró)

### Requirement: Anotarse a la carrera con resultado real del backend
El botón "Anotarse al llamado" DEBE crear la solicitud real idempotente (`POST /mesas/{id}/solicitudes` con `Idempotency-Key` persistida). Si la vacante se obtiene (201) la tarjeta muestra "¡Vacante reservada!"; si un competidor se adelantó (409) se muestra "Cupo agotado — alguien se anotó primero".

#### Scenario: Dos jugadores por una sola vacante
- **GIVEN** un llamado abierto con una sola vacante
- **WHEN** dos jugadores distintos se anotan a la vez
- **THEN** uno recibe 201 y la tarjeta lo muestra como reservado
- **AND** el otro recibe 409 y la tarjeta muestra el cupo agotado
- **AND** la ocupación final de la mesa no supera `jugadores_max`