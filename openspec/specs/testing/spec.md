# Purpose

Definir la suite de pruebas reproducibles que evidencia los comportamientos pedidos por AE2: caché con invalidación, carrera por la última vacante, idempotencia por `Idempotency-Key`, QR de asistencia single-use, reintentos con DLQ y salud `/ready`. La suite corre con `pytest` sobre bases `*_test` y Redis aislado (db 15).

## Requirements

### Requirement: Suite pytest reproducible
`pytest tests` DEBE ejecutarse desde la raíz del repo, contra `mesas_db_test` (PostgreSQL) y Redis db 15, dejando las DBs y Redis limpios entre tests y terminando en verde.

#### Scenario: Corrida completa
- **WHEN** se ejecuta `pytest tests -v` con las bases `*_test` disponibles
- **THEN** todos los archivos (cache, carrera, idempotencia, qr, dlq) pasan y el estado queda limpio entre tests

### Requirement: Evidencia de caché con invalidación
El test DEBE demostrar que la primera lectura de `GET /api/v1/mesas` consulta PostgreSQL y la segunda se sirve desde Redis (instrumentado), y que un write invalida el cache.

#### Scenario: Miss → hit → invalidación
- **WHEN** se hace `GET /api/v1/mesas` dos veces seguidas y luego un `POST` de mesa (write) y otro `GET`
- **THEN** la llamada a `listar_mesas` ocurre 1 vez en el primer GET y 1 vez nueva tras el write (el 2º GET no toca la DB)

### Requirement: Evidencia de la carrera por la última vacante
Con N solicitudes concurrentes sobre una mesa con 1 vacante, el test DEBE resultar en exactamente 1 `201` y N-1 `409`, con `jugadores_actuales <= jugadores_max`.

#### Scenario: 10 concurrentes, 1 vacante
- **WHEN** 10 `POST /mesas/{id}/solicitudes` concurrentes (una por jugador, con `Idempotency-Key` propia) contra una mesa con `jugadores_max=1`
- **THEN** un único `201`, nueve `409` y `jugadores_actuales == 1`

#### Scenario: Repro del bug documentado
- **WHEN** se consulta `tests/repro_carrera.py` (no recopilado por pytest)
- **THEN** documenta que sin las barreras (UPDATE condicional + SET NX) todos terminan en `201` y `jugadores_actuales > jugadores_max`

### Requirement: Evidencia de idempotencia por `Idempotency-Key`
Repetir la misma solicitud con la misma key DEBE devolver la misma respuesta sin ocupar una segunda vacante.

#### Scenario: Misma key repetida
- **WHEN** se hace dos veces `POST /mesas/{id}/solicitudes` con la misma `Idempotency-Key` contra una mesa de 1 vacante
- **THEN** ambas responden `201` con la misma respuesta y `jugadores_actuales == 1`

### Requirement: Evidencia de QR single-use
La segunda validación del mismo QR DEBE responder `409`.

#### Scenario: QR reutilizado
- **WHEN** se emite un QR para una sesión y se valida dos veces
- **THEN** la primera validación responde `200` y la segunda `409`

### Requirement: Evidencia de retry/DLQ
Un mensaje cuyo procesamiento falla DEBE reencolarse con `_intentos` incrementado y, tras los reintentos máximos, terminar en `dlq.general` con `ultimo_error` y `cola_origen`.

#### Scenario: Fallo simulado en el consumidor
- **WHEN** `_manejar` procesa un mensaje con un handler que siempre falla hasta superar `MAX_REINTENTOS`
- **THEN** el mensaje llega a `dlq.general` con `_intentos == 2`, `ultimo_error` con "fallo tras 3 reintentos" y `cola_origen` correcta