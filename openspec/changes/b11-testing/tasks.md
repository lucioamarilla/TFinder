## 1. Infraestructura de testing

- [x] 1.1 Bases `mesas_db_test`, `builds_db_test`, `feed_db_test`, `notif_db_test` en `infra/postgres-init/01-crear-dbs.sql` y creadas en la instancia
- [x] 1.2 `requirements-dev.txt` con pytest/httpx/ruff
- [x] 1.3 `pytest.ini` con `pythonpath = .`
- [x] 1.4 `tests/conftest.py`: pool/init en `mesas_db_test`, Redis db 15, truncates por test, tokens gm/jugador

## 2. Tests (done)

- [x] 2.1 `test_cache.py`: miss→hit con instrumentación y write que invalida
- [x] 2.2 `test_carrera.py`: 10 concurrentes / 1 vacante → 1×201 y 9×409
- [x] 2.3 `test_idempotencia.py`: misma `Idempotency-Key` → misma respuesta, 1 vacante ocupada
- [x] 2.4 `test_qr.py`: 2ª validación del mismo QR → 409
- [x] 2.5 `test_dlq.py`: fallo simulado → `dlq.general` tras `MAX_REINTENTOS`
- [x] 2.6 `tests/repro_carrera.py`: documenta el fallo sin barreras (no recopilado)
- [x] 2.7 Evidencia guardada en `AE2/evidencias/pytest-B11.txt`
- [x] 2.8 `openspec validate b11-testing`

## 3. Cierre de la tarea

- [ ] 3.1 Rama `f/B11_testing`, commit, merge y archivar
- [ ] 3.2 Cerrar issue GitHub #24