# Guía de pruebas manuales de TFinder

## 1. Objetivo y alcance

Esta guía permite verificar TFinder de punta a punta: Docker, infraestructura, datos demo, frontend, autenticación, API de mesas, solicitudes de unión, matchmaking, QR, builds, feed, wiki, PDFs, notificaciones, correo, eventos, DLQ, health checks y CI.

La guía se separa en:

- **Pruebas seguras:** no borran datos ni detienen servicios.
- **Pruebas avanzadas:** reinician Docker, pausan dependencias, modifican datos o reproducen fallos. Requieren confirmación antes de ejecutarse.

No usar datos reales. La aplicación y sus servicios están pensados para un entorno local de desarrollo.

## 2. Convenciones

Cada caso debe registrarse con:

- ID y nombre.
- Fecha y operador.
- Versión o commit, si corresponde.
- Precondiciones.
- Resultado: `PASS`, `FAIL`, `BLOCKED` o `N/A`.
- Evidencia: captura, respuesta HTTP, log o consulta SQL.

Los IDs de correlación se deben usar para relacionar frontend, APIs, eventos y email. Nunca reutilizar una `Idempotency-Key` entre pruebas independientes.

## 3. Prerrequisitos

- Docker Engine y Docker Compose.
- Python 3.11 o superior.
- Node.js y npm.
- `curl`, `jq` opcional y un navegador moderno.
- Puertos 5173, 8001, 8002, 8003, 8004, 5432, 5673, 6390, 8025 y 15673 libres.

## 4. Levantar el ambiente

Desde la raíz del proyecto:

```bash
docker compose up -d --build
docker compose ps
```

Servicios esperados:

| Servicio | URL o puerto |
|---|---|
| Frontend | http://localhost:5173 |
| Mesas API | http://localhost:8001/docs |
| Builds API | http://localhost:8002/docs |
| Feed API | http://localhost:8003/docs |
| Notificaciones API | http://localhost:8004/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6390 |
| RabbitMQ AMQP | localhost:5673 |
| RabbitMQ Management | http://localhost:15673 |
| MailHog | http://localhost:8025 |

Los cuatro endpoints de salud deben responder correctamente:

```bash
for port in 8001 8002 8003 8004; do
  curl -i "http://localhost:${port}/health"
  curl -i "http://localhost:${port}/live"
  curl -i "http://localhost:${port}/ready"
done
```

Esperado: cada API devuelve `200` en `/health`, `/live` y `/ready` cuando sus dependencias están disponibles.

## 5. Datos demo

Con `DEMO_SEED_ENABLED=true`, los datos se insertan una sola vez. La contraseña de todos los usuarios demo es:

```text
DemoTFinder123!
```

| Email | Uso |
|---|---|
| `admin@tfinder.dev` | Pruebas de administración |
| `gm@tfinder.dev` | Matchmaking y validación QR |
| `jugador1@tfinder.dev` | Jugador normal |
| `jugador2@tfinder.dev` | Concurrencia |
| `jugador3@tfinder.dev` | Concurrencia |
| `email_svc@tfinder.dev` | Usuario interno de notificaciones |

Verificación de filas:

```bash
docker exec tfinder-postgres psql -U tfinder -d mesas_db -c "SELECT id,nombre,estado,jugadores_actuales,jugadores_max FROM mesas ORDER BY id;"
docker exec tfinder-postgres psql -U tfinder -d mesas_db -c "SELECT id,email,rol FROM usuarios ORDER BY id;"
docker exec tfinder-postgres psql -U tfinder -d builds_db -c "SELECT id,nombre FROM builds ORDER BY id;"
docker exec tfinder-postgres psql -U tfinder -d feed_db -c "SELECT id,tipo FROM publicaciones ORDER BY id;"
docker exec tfinder-postgres psql -U tfinder -d notif_db -c "SELECT id,leida FROM notificaciones ORDER BY id;"
```

En una instalación limpia se esperan 3 mesas, 2 builds, 3 publicaciones, 3 notificaciones, 2 eventos y 2 páginas wiki. Ejecutar `docker compose up -d` nuevamente no debe duplicar registros.

## 6. Pruebas seguras del frontend

### M-01 Landing

1. Abrir `http://localhost:5173/`.
2. Verificar que la página cargue sin errores en DevTools.
3. Pulsar **Explorar Mesas**.
4. Confirmar que se abre `/mesas`.

Esperado: la navegación funciona y no se muestran datos ficticios en el listado real.

### M-02 Listado de mesas

1. Abrir `/mesas`.
2. Verificar que se muestren las mesas existentes.
3. Buscar por nombre.
4. Filtrar por sistema y disponibilidad.
5. Ordenar por nombre y estado.
6. Limpiar filtros.
7. Recargar la página.

Esperado: los filtros son de cliente, la lista conserva los datos de la API y una búsqueda sin resultados muestra estado vacío.

### M-03 Detalle de mesa

1. Abrir una mesa existente.
2. Confirmar nombre, sistema, descripción, estado y ocupación.
3. Abrir `/mesas/99999`.
4. Volver a una mesa válida.

Esperado: una mesa válida muestra información coherente y un ID inexistente muestra el estado de error controlado.

### M-04 Invitado e inicio de sesión

1. Abrir el detalle de una mesa sin sesión iniciada.
2. Pulsar la acción de unirse.
3. Confirmar redirección a `/login?redirect=/mesas/<id>`.
4. Iniciar sesión con un usuario demo.
5. Confirmar regreso a la mesa.

Esperado: el usuario no pierde el destino de la acción.

### M-05 Registro

1. Abrir `/registro`.
2. Completar email válido, nombre y contraseña de al menos 8 caracteres.
3. Enviar.
4. Iniciar sesión con el usuario creado.
5. Cerrar sesión.

Esperado: la cuenta creada puede autenticarse. Un email duplicado muestra error sin sobrescribir la cuenta existente. La cuenta siempre nace con rol `usuario`, aunque la petición envíe otro valor en el campo `rol`.

### M-06 Sesión y logout

1. Iniciar sesión.
2. Recargar el navegador.
3. Verificar que la sesión continúe.
4. Cerrar sesión.
5. Intentar volver a una página protegida.

Esperado: refresh mantiene sesión y logout elimina el estado local.

## 7. Funciones activas y pantallas “Próximamente”

### 7.1 Funciones activas

Las siguientes funciones están habilitadas y deben ser operativas desde el frontend:

- Crear mesa (`/mesas/nueva`) y editar mesa (`/mesas/:id/editar`).
- Asistencia por QR (`/mesas/:id/sesiones/:sesionId/qr`).
- Matchmaking (`/matchmaking`).
- Recuperación de contraseña (`/recuperar`).
- Notificaciones (`/notificaciones`): la campana del header debe llevar a `/notificaciones` (no a Próximamente) y el listado debe provenir de la API en el puerto 8004.
- Encuentros (`/encuentros`): accessible desde la navegación, calcula el grupo en el navegador y no persiste.

Comprobar que cada pantalla carga sin el estado **Próximamente** y que las operaciones persisten contra el backend correspondiente (mesas-api 8001, notif-api 8004).

La campana del header debe mostrar el contador de avisos sin leer, actualizado al menos cada 5 segundos. Si notif-api no responde, la campana se atenúa y el contador queda en cero.

### 7.2 Pantallas “Próximamente”

Las siguientes funciones están deshabilitadas intencionalmente. Al abrir cualquiera de sus URLs se debe mostrar **Próximamente** y el enlace para volver a explorar mesas:

- Dashboard.
- Perfil extendido.
- Mis campañas.
- Gestión de campaña.
- Wiki de campaña.
- Calendario y votación.
- Sesiones y diario.
- Gestión de jugadores.
- Builds.
- Feed Social.
- Directorio de aventureros.
- Tags.
- Administración.

Comprobar también las subrutas específicas de wiki, sesiones, builds y administración. El bloqueo del frontend no sustituye la autorización de los endpoints backend.

## 8. Autenticación API

Base: `http://localhost:8001/api/v1/auth`.

Obtener tokens:

```bash
ACCESS=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"jugador1@tfinder.dev","password":"DemoTFinder123!"}' | jq -r .access_token)

REFRESH=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"jugador1@tfinder.dev","password":"DemoTFinder123!"}' | jq -r .refresh_token)
```

Casos:

| ID | Caso | Esperado |
|---|---|---|
| A-01 | Login válido | `200` con access y refresh token |
| A-02 | Password incorrecto | `401` con mensaje genérico |
| A-03 | Email inexistente | `401` con el mismo mensaje que password incorrecto |
| A-04 | `/auth/me` con token | `200` con email, rol y expiración |
| A-05 | `/auth/me` sin token | `401` |
| A-06 | Token malformado | `401` |
| A-07 | Refresh válido | `200` con nuevo access token |
| A-08 | Access como refresh | `401` |
| A-09 | Refresh como access | `401` |
| A-10 | Logout | `200`, después el token queda revocado |
| A-11 | Admin-only como admin | `200` |
| A-12 | Admin-only como usuario | `403` |
| A-13 | Registro enviando `rol: "admin"` | `201` pero la cuenta queda con rol `usuario` |
| A-14 | Login de esa cuenta y `/auth/admin-only` | `403` |

El registro es público y siempre crea cuentas con rol `usuario`: los roles `gm` y `admin` se otorgan fuera de esa vía (seed demo o administración). A-13 y A-14 cubren que el endpoint no sea una vía de escalada de privilegios.

Usar siempre un `X-Correlation-Id` diferente por caso.

## 9. Mesas API

Base: `http://localhost:8001/api/v1`.

| ID | Caso | Esperado |
|---|---|---|
| ME-01 | Listar mesas | `200` y array de mesas |
| ME-02 | Obtener mesa existente | `200` |
| ME-03 | Obtener mesa inexistente | `404` con envelope de error |
| ME-04 | Crear mesa autenticado | `201` |
| ME-05 | Crear sin token | `401` |
| ME-06 | Crear sin campos obligatorios | `400` |
| ME-07 | Crear con estado inválido | `400` |
| ME-08 | Actualizar parcialmente | `200`, solo cambia lo enviado |
| ME-09 | Actualizar inexistente | `404` |
| ME-10 | Eliminar mesa temporal | `204`, luego detalle `404` |
| ME-11 | Listar miembros | `200` con `mesa_id` y miembros |
| ME-12 | Miembros sin token | `401` |

No crear ni borrar mesas reales en una base compartida. Para la prueba de eliminación, crear una mesa de prueba y anotar su ID.

## 10. Solicitud de unión

Endpoint principal: `POST /api/v1/mesas/{id}/solicitudes`.

1. Iniciar sesión como jugador.
2. Elegir mesa abierta con vacante.
3. Enviar `Idempotency-Key` única y body `{}`.
4. Repetir exactamente la misma solicitud.
5. Probar mesa llena.
6. Probar mesa inexistente.
7. Probar sin token.

Esperado: la primera unión devuelve `201`; la repetición no duplica la solicitud; falta de capacidad devuelve `409`; recursos inexistentes y falta de autenticación producen el error correspondiente.

Probar también `POST /api/v1/mesas/{id}/solicitar`, que es legacy y devuelve `202`; no usarlo para comprobar la reserva atómica de una vacante.

### Concurrencia

Sobre una mesa con una sola vacante, enviar solicitudes simultáneas con usuarios y keys diferentes. Esperado: como máximo un `201`; las restantes `409`; el contador nunca supera el máximo.

## 11. Matchmaking y QR

### Matchmaking

1. Login como `gm@tfinder.dev`.
2. Abrir `/api/v1/matchmaking/{mesa_id}/abrir`.
3. Consultar `/api/v1/matchmaking/{mesa_id}/estado`.
4. Repetir como usuario normal.
5. Consultar expiración después del TTL.

Esperado: GM abre el llamado, usuarios no GM reciben `403`, el estado muestra TTL y al expirar queda cerrado.

### QR

1. Localizar una sesión abierta.
2. Emitir `POST /api/v1/sesiones/{id}/qr`.
3. Validar como GM con el mismo `usuario_id` y `qr_data`.
4. Repetir la validación.
5. Alterar el QR o cambiar el usuario.

Esperado: primer uso registra asistencia; segundo uso `409`; QR alterado, expirado o asociado a otra persona no registra asistencia.

## 12. Builds y feed

### Builds

- `GET http://localhost:8002/api/v1/builds` devuelve los builds.
- Filtrar por mesa inexistente devuelve lista vacía, no error.
- `/builds/1` devuelve detalle y un ID inexistente devuelve `404`.
- `GET /api/v1/tags` devuelve tags.
- `POST /api/v1/builds/1/pdf` requiere token y devuelve `202` con `documento_id`.

### Feed y wiki

- `GET http://localhost:8003/api/v1/feed` devuelve publicaciones.
- `GET /api/v1/wiki` devuelve carpetas y páginas.
- `GET /api/v1/wiki?mesa_id=demo-mesa` devuelve las páginas seed.
- Una mesa inexistente devuelve estructura vacía.
- `POST /api/v1/mesas/demo-mesa/sesiones/1/diario/pdf` devuelve `202`.

## 13. PDFs asíncronos

Después de solicitar un PDF:

```bash
curl -i "http://localhost:8004/api/v1/pdf/<documento_id>/estado"
curl -f -o documento.pdf "http://localhost:8004/api/v1/pdf/<documento_id>"
file documento.pdf
```

Esperado: el estado progresa a `listo` y la descarga responde `application/pdf`. Un PDF solicitado sin autenticación debe rechazarse. Un evento inválido no debe producir un documento descargable.

## 14. Notificaciones, SSE y email

notif-api exige sesión: `GET /notificaciones`, `PATCH /notificaciones/{id}/leida` y `/notificaciones/stream` devuelven `401` sin token. Los avisos se filtran por el usuario del token (más los generales, que no tienen destinatario), y `PATCH` sobre un aviso de otro usuario devuelve `404`.

Las rutas de operación son solo de admin (`dlq`, `emails`, `event-log`): `401` sin token, `403` con rol `gm` o `usuario`, `200` con `admin`.

```bash
NOTIF=http://localhost:8004
ACCESS=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"jugador1@tfinder.dev","password":"DemoTFinder123!"}' | jq -r .access_token)
ADMIN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@tfinder.dev","password":"DemoTFinder123!"}' | jq -r .access_token)
```

| ID | Caso | Esperado |
|---|---|---|
| N-01 | `GET /api/v1/notificaciones` sin token | `401` |
| N-02 | `GET /api/v1/notificaciones` con `ACCESS` | `200` con los avisos del usuario y los generales |
| N-03 | `GET /api/v1/notificaciones?solo_no_leidas=true` | filtra por `leida` |
| N-04 | `PATCH /api/v1/notificaciones/{id}/leida` sin token | `401` |
| N-05 | `PATCH` de un aviso de otro usuario | `404` y el aviso sigue sin leerse |
| N-06 | Un ID inexistente | `404` |
| N-07 | `GET /api/v1/notificaciones/stream` sin token | `401` |
| N-08 | `GET /api/v1/dlq` con rol no admin | `403` (con `ADMIN`, `200`) |
| N-09 | `GET /api/v1/event-log` con rol no admin | `403` (con `ADMIN`, `200`) |
| N-10 | `GET /api/v1/emails` con rol no admin | `403` (con `ADMIN`, `200`) |
| N-11 | `GET /api/v1/pdf/{id}` sin token | `401` |
| N-12 | `POST /api/v1/auth/recuperar` | `202` y el correo aparece en MailHog |

Ademas: publicar un evento `mesa.aceptada` o `sesion.confirmada` debe crear registro y notificar mediante SSE, y `GET /api/v1/event-log?correlation_id=<id>` debe relacionar el evento (solo con `ADMIN`).

## 15. RabbitMQ y DLQ

En RabbitMQ Management se esperan los exchanges `tfinder.events` y `tfinder.dlx`, y las colas `notif.mesa`, `notif.sesion`, `doc.pdf` y `dlq.general`.

La guía avanzada debe publicar un evento PDF inválido y verificar:

1. Primer fallo.
2. Reintento tras backoff.
3. Segundo fallo.
4. Tercer intento.
5. Publicación en `dlq.general`.
6. Registro en `notif_db.mensaje_dlq`.
7. Consulta en `GET /api/v1/dlq`.
8. Reintento o descarte por ID.

No presentar `202` como prueba de que el PDF ya está listo: siempre consultar estado y descarga.

## 16. Pruebas avanzadas destructivas

Ejecutar solo con autorización y sin datos reales.

### Reinicio limpio

```bash
docker compose down -v
docker compose up -d --build
```

Verificar que las cuatro bases se recrean, los seeds se cargan una vez y todos los servicios vuelven a `healthy`.

### Dependencia caída

Pausar una dependencia, consultar readiness y restaurarla:

```bash
docker pause tfinder-redis
curl -i http://localhost:8001/ready
docker unpause tfinder-redis

docker pause tfinder-rabbitmq
curl -i http://localhost:8002/ready
docker unpause tfinder-rabbitmq

docker pause tfinder-postgres
curl -i http://localhost:8003/ready
docker unpause tfinder-postgres
```

Esperado: `503` y estado degradado mientras la dependencia está pausada; `200` y listo después de restaurarla.

### Fallo SMTP

```bash
docker pause tfinder-mailhog
# ejecutar recuperación o reintento de email
docker unpause tfinder-mailhog
```

Verificar estado `fallido`, error registrado y recuperación del envío tras restaurar MailHog.

### QR e idempotencia expirados

Esperar el TTL correspondiente o usar una instancia aislada. Confirmar que un QR vencido no valida y que una solicitud repetida después de la expiración de Redis puede crear una nueva operación.

## 17. Seguridad y casos borde

Verificar y documentar el resultado real, sin marcar como seguro lo que no lo está:

- Token ausente, vencido, malformado o revocado.
- Rol insuficiente.
- Acceso directo a endpoints restringidos.
- Usuario normal intentando abrir matchmaking.
- Registro requesting rol `gm` o `admin`.
- Cualquier usuario intentando modificar una mesa.
- Acceso directo a notificaciones, email, event log y DLQ.
- Diferencia entre bloqueo visual de frontend y autorización backend.
- CORS entre orígenes.
- Password corta, email inválido, campos desconocidos y JSON malformado.
- Intentos repetidos de QR, eventos e idempotencia.
- Datos seed y credenciales solo en desarrollo.

## 18. Verificación final

```bash
venv/bin/pytest -m unit -q
venv/bin/pytest -m integration -q
venv/bin/ruff check .
cd tfinder-vue
npm run lint
npm run type-check
npm run test:unit -- --run
npm run test:integration -- --run
npm run build
```

Registrar cualquier diferencia entre el resultado esperado y el observado. Las brechas conocidas no deben ocultarse: deben reportarse como `FAIL` o `BLOCKED` con evidencia y referencia al endpoint afectado.
