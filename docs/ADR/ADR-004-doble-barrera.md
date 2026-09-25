# ADR-004 · Doble barrera para la carrera por la última vacante

- Estado: **Aceptado**
- Fecha: 2026-09-23

## Contexto

Varios jugadores pueden solicitar, en paralelo, la última vacante de una mesa. Sin control, dos lecturas simultáneas ven `jugadores_actuales < jugadores_max` y ambos INSERTan, dejando `jugadores_actuales > jugadores_max` (bug documentado en `tests/repro_carrera.py`). Se descartó:

- `SELECT ... FOR UPDATE`: requiere transacción sin cerrar entre lectura y escritura, expande el lock y complica el pool.
- Lock de tabla: serializa toda la mesa, excesivo y ajeno al patrón de los pools.

## Decisión

**Doble barrera** (`reservar` en `mesas_api/app/services/vacante.py` + `ocupar_vacante` en `models/mesa.py`):

1. **Barrera Redis (`SET NX EX 60`)**: un solo request puede entrar a la sección crítica por mesa; el resto responde `409 SolicitudEnProcesoError` (maneja el "otro se está procesando").
2. **Barrera PostgreSQL (`UPDATE mesas SET jugadores_actuales = jugadores_actuales + 1 WHERE id = %s AND jugadores_actuales < jugadores_max RETURNING id`)**: check-and-set atómico; Postgres toma el lock de fila hasta el commit y solo la transacción que pasa el `WHERE` gana el cupo.

Encima se apoya la **idempotencia por `Idempotency-Key`** (B05/B06): la misma key repetida devuelve el mismo resultado sin volver a ocupar vacante (`idem:solicitud:{key}` en Redis).

## Consecuencias

- **Positivas**: invariante garantizado (`jugadores_actuales <= jugadores_max`), evidencia de concurrencia reproducible con `pytest` (10 concurrentes → 1×201 / 9×409), sin locks largos de transacción; cada capa tiene TTL/rollback propio (Redis expira, Postgres revierte).
- **Negativas**: dos sistemas a mantener en el path crítico (nuevo fallo si Redis y Postgres no coinciden); la reserva Redis introduce un segundo punto de falla; requiere prueba de estrés periódica (B11) para no regresionar.