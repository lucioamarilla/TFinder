# Purpose

Conectar la acción "unirse a una mesa" del frontend con la doble barrera de B06: solicitud real contra `POST /api/v1/mesas/{id}/solicitudes`, `Idempotency-Key` persistida por `(mesa, usuario)` para reenvíos sin doble efecto, y visibilidad de la carrera por la última vacante (201 gana / 409 cupo agotado).

## Requirements

### Requirement: Solicitud real con Idempotency-Key persistida
`mesasApi.solicitarUnion` DEBE enviar la solicitud a `/api/v1/mesas/{id}/solicitudes` con `Authorization` y la `Idempotency-Key` provista. El composable `useSolicitud` DEBE persistir la key por `(mesa, usuario)` en `localStorage` y reutilizarla en reintentos del mismo usuario, de modo que el reenvío no ocupe una segunda vacante.

#### Scenario: Reenvío accidental del mismo usuario
- **WHEN** el mismo usuario repite la solicitud con la misma key tras un `201`
- **THEN** el backend devuelve el mismo resultado y la ocupación de la mesa no vuelve a incrementarse

### Requirement: Estados visibles de la carrera
`MesaDetailView` DEBE reflejar `enviando → solicitada | agotada | error` en el botón (deshabilitado + `aria-busy` mientras envía), mostrar el mensaje del backend en `409` (cupo agotado) y marcar la "última vacante en disputa" cuando queda un solo puesto.

#### Scenario: Dos jugadores por la última vacante
- **WHEN** hay una vacante y dos usuarios solicitan a la vez
- **THEN** uno recibe `201` (solicitada) y el otro `409` (cupo agotado) con el mensaje del backend visible