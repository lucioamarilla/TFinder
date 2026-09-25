# Proposal: Testing automatizado y evidencia de concurrencia

## Why

Criterio AE2 de reproductibilidad: las garantías de B03–B09 (caché+invalidación, carrera por la última vacante con doble barrera, idempotencia por key, QR single-use, retry/DLQ, `/ready`) deben quedar cubiertas con pytest y evidencias reproducibles para el Portafolio.

## What Changes

- **`tests/` nuevo**: `conftest.py` (pool/init sobre `mesas_db_test`, Redis en db 15, truncates por test, tokens gm/jugador), `test_cache.py`, `test_carrera.py`, `test_idempotencia.py`, `test_qr.py`, `test_dlq.py` y `repro_carrera.py` (documentación del bug sin solución, no recopilable).
- **`pytest.ini`**: `pythonpath = .` (imports de `app/`, `mesas_api`, `notif_api`).
- **`requirements-dev.txt`**: ya listo (`pytest`, `httpx`, `ruff`).
- **`infra/postgres-init/01-crear-dbs.sql`**: agrega `*_test` idempotentes (`mesas_db_test`, `builds_db_test`, `feed_db_test`, `notif_db_test`). Creadas además en la instancia en ejecución.
- **Evidencia**: `AE2/evidencias/pytest-B11.txt` con `pytest tests -v` (5 passed) y la corrida específica de la carrera.

## Capabilities

- **New Capabilities**: `testing` — suite pytest reproducible (verde) que evidencia caché, concurrencia, idempotencia, single-use y DLQ.
- **Modified Capabilities**: ninguna (no cambia código de producto; `postgres-init` solo suma bases de test).

## Impact

- Las DBs de test quedan aisladas de las de desarrollo (`*_db_test`, Redis db 15). El DLQ test lee/consume solo mensajes con `event_id` propio y ack de vuelta, sin perturbar colas reales.