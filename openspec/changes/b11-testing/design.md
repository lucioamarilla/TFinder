# Design: Testing automatizado

## Context

El producto (REST FastAPI + pika workers) se prueba contra la misma infraestructura local real (postgres/redis/rabbitmq publicados por compose en localhost) pero con bases y DB de Redis aisladas, de modo que ninguna corrida contamina los ambientes de desarrollo.

## Decisions

**D1 — Bases de test aisladas.**
`mesas_db_test` (y las otras `*_test`) creadas en `postgres-init/01-crear-dbs.sql` (idempotente). `conftest.py` define `MESAS_DATABASE_URL`, `NOTIF_DATABASE_URL`, `REDIS_URL` (db 15) y `JWT_SECRET=dev-secret` con `setdefault` ANTES de importar los módulos que leen env al cargarse (`mesas_api.app.db`, `app.infra.redis`, `models.auth_model`).

**D2 — Pool y esquema por sesión de pytest.**
Fixture `bd_pruebas` (session): `abrir_pool()` + `init_db()` (crea tablas en `mesas_db_test`). No se usa `TestClient` como context manager: el lifespan de FastAPI llama `cerrar_pool()`, que cierra el pool singleton y rompería el siguiente test (PoolClosed). Cada test hace `TRUNCATE <tablas> RESTART IDENTITY CASCADE` + `flushdb` antes y después.

**D3 — Tokens reales.**
Gm y jugadores se registran por `/api/v1/auth/register`+`/login` (PBKDF2 de 120k iteraciones): el test valida el circuito completo de auth, no tokens fabricados. La validación de QR usa el `sub` real del jugador.

**D4 — Carrera con concurrencia real.**
`ThreadPoolExecutor(max_workers=10)`; cada worker dispara con su propio `TestClient` (mismo app en proceso). La 2ª barrera (`reservar` SET NX + `ocupar_vacante` UPDATE condicional) garantiza 1×201 / 9×409. `repro_carrera.py` queda fuera del colección de pytest (sin prefijo `test_`) documentando el fallo sin soluciones.

**D5 — DLQ sin perturbar productores.**
Se conduce `_manejar` de `notif_api` con un canal fake y `time.sleep` monkeypatcheado; `_republicar`/`_enviar_dlq` usan RabbitMQ real. Se verifica la llegada a `dlq.general` leyendo solo mensajes con `event_id` propio (ack) y requeueando el resto.

**D6 — Evidencia portafolio.**
`pytest tests -v` completo y la corrida específica de la carrera se guardan en `AE2/evidencias/pytest-B11.txt`.

## Risks

- **PBKDF2 con 120k iteraciones**: el registro/login en tests agrega ~0,2 s por usuario; aceptable (13 s total).
- **RabbitMQ local requerido**: si rabbitmq está caído, la suite de DLQ falla. Documentado en requirements (infra local de B01).
- **Pool de 5 conexiones con 10 hilos**: ops cortas; el pool serializa esperas sin timeouts (30 s default), las corridas verdes lo confirman.

## Migration Plan

1. Crear bases `*_test` + sumar al init de postgres.
2. Escribir conftest + los 5 tests + `repro_carrera.py` + `pytest.ini`.
3. Correr `pytest tests -v` → verde; capturar evidencia en `AE2/evidencias/`.
4. Rama, commit, merge, archivar, cerrar #24.

## Verification

- `pytest tests -v` → 5 passed.
- `pytest tests/test_carrera.py -v` → 1 passed (1×201 / 9×409).
- `openspec validate b11-testing` → válido.