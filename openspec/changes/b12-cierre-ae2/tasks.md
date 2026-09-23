## 1. ADR

- [x] 1.1 ADR-001 PostgreSQL multi-DB
- [x] 1.2 ADR-002 Redis TTL/invalidación
- [x] 1.3 ADR-003 RabbitMQ + DLQ
- [x] 1.4 ADR-004 Doble barrera concurrencia
- [x] 1.5 ADR-005 MailHog/outbox
- [x] 1.6 ADR-006 Separación en servicios
- [x] 1.7 ADR-007 QR single-use

## 2. OpenAPI

- [x] 2.1 `/docs` y `/openapi.json` 200 en los 4 servicios
- [x] 2.2 Sin `$ref` huérfanos (mesas 18, builds 7, feed 5, notif 9 rutas)

## 3. Evidencias

- [x] 3.1 `scripts/generar_evidencias.py` (regenera PNG/txt contra el sistema)
- [x] 3.2 9 PNG en `AE2/evidencias/` (redis, rabbit/dlq, carrera, email, qr, pdf, logs, ready, pytest)
- [x] 3.3 `EVIDENCIAS.md` índice criterio → archivo

## 4. Entrega y repo

- [x] 4.1 `AE2/README.md` de entrega (estado, cómo correr, enlaces)
- [x] 4.2 `openspec validate b12-cierre-ae2`
- [ ] 4.3 Rama `f/B12_cierre_ae2`, commit, merge y archivar spec a `openspec/specs/cierre-ae2`
- [ ] 4.4 Tags `2.0.0` (alfa) y `2.1.0` (beta); cerrar issue #25