# Tutorial de pruebas de TFinder AE2

Guía de referencia para probar **todo** lo que se puede probar en el sistema. Cada caso
trae la URL exacta, el dato que hay que cargar, en qué campo va, y qué se espera.

Cómo se lee cada caso:

| Columna | Significado |
|---|---|
| **URL** | Dirección completa a abrir o a llamar |
| **Método** | Verbo HTTP |
| **Campo** | Dónde se carga el dato (header, query, body JSON, formulario web) |
| **Dato** | Valor exacto a escribir |
| **Esperado** | Código HTTP y cuerpo de respuesta |

Las credenciales son **solo de desarrollo local**. Nunca usarlas en producción.

---

## 0. Preparación

### 0.1 Levantar el ambiente

```bash
cd TFinder
docker compose up -d --build
docker compose ps
```

Todos los contenedores deben quedar `Up` y las dependencias de infraestructura `healthy`.

### 0.2 Las 4 cuentas para probar

Contraseña de **todas**: `DemoTFinder123!`

| # | Email | Rol | Sirve para probar |
|---:|---|---|---|
| 1 | `admin@tfinder.dev` | `admin` | Endpoints exclusivos de admin (DLQ, emails, event-log) |
| 2 | `gm@tfinder.dev` | `gm` | Abrir matchmaking, emitir y validar QR |
| 3 | `jugador1@tfinder.dev` | `usuario` | Flujo de jugador normal |
| 4 | `jugador2@tfinder.dev` | `usuario` | Concurrencia y segunda víctima |
| 5 | `jugador3@tfinder.dev` | `usuario` | Tercera víctima de la carrera |
| 6 | `email_svc@tfinder.dev` | `usuario` | Usuario interno del servicio de email |

### 0.3 Tableros de control

| Qué | Dónde | Credenciales |
|---|---|---|
| Documentación interactiva de las APIs | `http://localhost:8001/docs` (y 8002, 8003, 8004) | — |
| Panel web del frontend | `http://localhost:5173` | — |
| RabbitMQ (colas en vivo) | `http://localhost:15673` | `tfinder` / `tfinder` |
| Bandeja de emails recibidos | `http://localhost:8025` | — |
| DBeaver → PostgreSQL | `localhost:5432` | `tfinder` / `tfinder` |

### 0.4 Los 3 datos de mesa que hay cargados

| ID | Nombre | Estado | Ocupación |
|---:|---|---|---|
| 1 | Mesa Demo Abierta | `abierta` | 2 de 4 → **2 vacantes** |
| 2 | Mesa Demo Casi Llena | `abierta` | 3 de 4 → **1 vacante** |
| 3 | Mesa Demo Cerrada | `cerrada` | 0 de 6 |

### 0.5 Herramienta para llamar la API

Con `curl` + `jq` (los casos de abajo usan esta forma):

```bash
curl -s -w '\n[HTTP %{http_code}]\n' -X POST http://localhost:8001/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"jugador1@tfinder.dev","password":"DemoTFinder123!"}' | jq
```

Alternativa: usar `/docs` de cada API, que tiene un botón **Try it out** por endpoint.

---

## 1. Tokens (se usan en casi todos los casos siguientes)

### 1.1 Obtener access token

| | |
|---|---|
| **URL** | `POST http://localhost:8001/api/v1/auth/login` |
| **Campo** | Body JSON |
| **Dato** | `{"email": "jugador1@tfinder.dev", "password": "DemoTFinder123!"}` |
| **Esperado** | `200` con `access_token` y `refresh_token` |

Guardar el token para reutilizarlo:

```bash
ACCESS=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"jugador1@tfinder.dev","password":"DemoTFinder123!"}' | jq -r .access_token)

ADMIN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@tfinder.dev","password":"DemoTFinder123!"}' | jq -r .access_token)

GM=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"gm@tfinder.dev","password":"DemoTFinder123!"}' | jq -r .access_token)
```

> Cada token dura 24 h y **cambia en cada login** (lleva un `jti` aleatorio). Si un caso
> falla con `401 Sesión revocada o expirada`, sacar un token nuevo.

### 1.2 Refresh token

| | |
|---|---|
| **URL** | `POST http://localhost:8001/api/v1/auth/refresh` |
| **Campo** | Body JSON → `refresh_token` |
| **Dato** | El `refresh_token` del login |
| **Esperado** | `200` con un **nuevo** `access_token` |

---

## 2. Autenticación (mesas-api, puerto 8001)

Base: `http://localhost:8001/api/v1/auth`

### 2.1 Registrar una cuenta nueva

| | |
|---|---|
| **URL** | `POST http://localhost:8001/api/v1/auth/register` |
| **Campo** | Body JSON: `email`, `password`, `nombre` |
| **Dato** | `{"email":"prueba1@tfinder.dev","password":"secreto123","nombre":"Prueba Uno"}` |
| **Esperado** | `201` con `access_token` y `refresh_token` |

> El `email` tiene que ser **nuevo**. Si ya existe, la respuesta es
> `400 El email ya está registrado` y **la cuenta original no se toca**: un `login` con la
> contraseña vieja sigue funcionando.

Reglas del campo:

| Campo | Regla | Si se rompe |
|---|---|---|
| `email` | Debe tener `@` | `400 body.email: value is not a valid email address: An email address must have an @-sign.` |
| `password` | Mínimo **8** caracteres | `400 body.password: String should have at least 8 characters` |
| `nombre` | Obligatorio | `400 body.nombre: Field required` |
| `rol` | Opcional. **Se ignora siempre** | La cuenta nace como `usuario` |

> **Prueba de escalada de privilegios:** mandar `"rol":"admin"` en el registro. La respuesta
> es `201`, pero el rol real sigue siendo `usuario`. Confirmar con `GET /auth/me`.

### 2.2 Login

| | |
|---|---|
| **URL** | `POST http://localhost:8001/api/v1/auth/login` |
| **Campo** | Body JSON: `email`, `password` |
| **Dato** | `{"email":"admin@tfinder.dev","password":"DemoTFinder123!"}` |
| **Esperado** | `200` con `access_token` y `refresh_token` |

### 2.3 Ver quién soy

| | |
|---|---|
| **URL** | `GET http://localhost:8001/api/v1/auth/me` |
| **Campo** | Header `Authorization` |
| **Dato** | `Authorization: Bearer <ACCESS>` |
| **Esperado** | `200` con `sub`, `rol`, `email`, `tipo`, `jti` |

### 2.4 Endpoint exclusivo de admin

| | |
|---|---|
| **URL** | `GET http://localhost:8001/api/v1/auth/admin-only` |
| **Campo** | Header `Authorization` |
| **Dato** | Con token de `admin@tfinder.dev` |
| **Esperado** | `200` con `{"ok":true}` |

### 2.5 Logout

| | |
|---|---|
| **URL** | `POST http://localhost:8001/api/v1/auth/logout` |
| **Campo** | Header `Authorization` |
| **Dato** | `Authorization: Bearer <ACCESS>` |
| **Esperado** | `200` con `{"ok":true}`. El token usado ahí queda revocado |

---

## 3. Matriz completa de casos de seguridad

Todos devuelven el mismo envelope de error:

```json
{"error": {"codigo": 401, "mensaje": "Autenticación requerida"}}
```

| # | URL | Método | Campo | Dato | Esperado |
|---:|---|---|---|---|---|
| S-01 | `/api/v1/auth/me` (8001) | GET | — | sin header | `401 Autenticación requerida` |
| S-02 | `/api/v1/auth/me` (8001) | GET | `Authorization` | `Bearer no.es.un.jwt` | `401 Token inválido o expirado` |
| S-03 | `/api/v1/auth/me` (8001) | GET | `Authorization` | refresh token en vez de access | `401 Use the access_token` |
| S-04 | `/api/v1/auth/refresh` (8001) | POST | body `refresh_token` | mandar el access token | `401 Use el refresh_token` |
| S-05 | `/api/v1/auth/login` (8001) | POST | body `password` | `passwordincorrecta123` | `401 Credenciales inválidas` |
| S-06 | `/api/v1/auth/login` (8001) | POST | body `email` | `nadie@tfinder.dev` | `401 Credenciales inválidas` (idéntico a S-05: no enumera usuarios) |
| S-07 | `/api/v1/auth/admin-only` (8001) | GET | `Authorization` | token de `usuario` | `403 Rol insuficiente` |
| S-08 | `/api/v1/auth/admin-only` (8001) | GET | `Authorization` | token de `gm` | `403 Rol insuficiente` |
| S-09 | `/api/v1/auth/admin-only` (8001) | GET | `Authorization` | token de `admin` | `200 {"ok":true}` |
| S-10 | `/api/v1/mesas/1/miembros` (8001) | GET | `Authorization` | sin header | `401` |
| S-11 | `/api/v1/mesas` (8001) | POST | body completo | sin header | `401` |
| S-12 | `/api/v1/builds/1/pdf` (8002) | POST | body `{}` | sin header | `401` |
| S-13 | `/api/v1/mesas/1/sesiones/1/diario/pdf` (8003) | POST | body `{}` | sin header | `401` |
| S-14 | `/api/v1/notificaciones` (8004) | GET | `Authorization` | sin header | `401` |
| S-15 | `/api/v1/notificaciones/stream` (8004) | GET | `Authorization` | sin header | `401` |
| S-16 | `/api/v1/dlq` (8004) | GET | `Authorization` | token de `usuario` | `403 Rol insuficiente` |
| S-17 | `/api/v1/dlq` (8004) | GET | `Authorization` | token de `gm` | `403 Rol insuficiente` |
| S-18 | `/api/v1/event-log` (8004) | GET | `Authorization` | token de `usuario` | `403 Rol insuficiente` |
| S-19 | `/api/v1/emails` (8004) | GET | `Authorization` | token de `usuario` | `403 Rol insuficiente` |
| S-20 | `/api/v1/matchmaking/1/abrir` (8001) | POST | `Authorization` | token de `usuario` | `403 Rol insuficiente` |
| S-21 | `/api/v1/ruta-que-no-existe` (cualquiera) | GET | — | — | `404 Recurso no encontrado` |
| S-22 | `/api/v1/builds/1/pdf` (8002) | **GET** en vez de POST | — | — | `405 Método no permitido para este endpoint` |
| S-23 | `/api/v1/auth/register` (8001) | POST | body `email` | un email ya registrado | `400 El email ya está registrado`, sin tocar la cuenta original |
| S-24 | `/api/v1/auth/register` (8001) | POST | body `password` | `"123"` | `400 body.password: String should have at least 8 characters` |
| S-25 | `/api/v1/auth/register` (8001) | POST | body `email` | `"no-es-email"` | `400 body.email: value is not a valid email address` |
| S-26 | `/api/v1/mesas` (8001) | POST | body `nombre` | omitir `nombre` | `400 body.nombre: Field required` |
| S-27 | `/api/v1/mesas` (8001) | POST | body `estado` | `"inventado"` | `400 body.estado: Input should be 'abierta' or 'cerrada'` |
| S-28 | `/api/v1/mesas` (8001) | POST | body `jugadores_max` | `0` | `400 body.jugadores_max: Input should be greater than 0` |
| S-29 | `/api/v1/builds/abc` (8002) | GET | path `build_id` | `abc` | `400 path.build_id: Input should be a valid integer` |
| S-30 | `/api/v1/feed?tipo=inventado` (8003) | GET | query `tipo` | `inventado` | `400`: tipo desconocido, no filtra en silencio |
| S-31 | `/api/v1/feed?limit=0` (8003) | GET | query `limit` | `0` | `400 limit debe estar entre 1 y 100` |

> S-22: la URL existe pero solo acepta POST. Es la forma de comprobar que el envelope
> también se normaliza en los errores que genera el router.

---

## 4. Mesas (mesas-api, puerto 8001)

Base: `http://localhost:8001/api/v1`

### 4.1 Listar mesas

| | |
|---|---|
| **URL** | `GET http://localhost:8001/api/v1/mesas` |
| **Campo** | — |
| **Dato** | — |
| **Esperado** | `200` con un array de 3 mesas |

### 4.2 Ver una mesa

| | |
|---|---|
| **URL** | `GET http://localhost:8001/api/v1/mesas/1` |
| **Campo** | Path: `mesa_id` |
| **Dato** | `1` |
| **Esperado** | `200` con nombre, sistema, estado y ocupación |

### 4.3 Mesa inexistente

| | |
|---|---|
| **URL** | `GET http://localhost:8001/api/v1/mesas/99999` |
| **Campo** | Path: `mesa_id` |
| **Dato** | `99999` |
| **Esperado** | `404 Mesa 99999 no encontrada` |

### 4.4 Crear mesa

| | |
|---|---|
| **URL** | `POST http://localhost:8001/api/v1/mesas` |
| **Campo** | Header `Authorization` + body JSON |
| **Dato** | Ver tabla de campos abajo |

```bash
curl -s -X POST http://localhost:8001/api/v1/mesas \
  -H "Authorization: Bearer $GM" -H 'Content-Type: application/json' \
  -d '{"nombre":"Mesa de Pruebas","sistema":"PF1e","descripcion":"Mesa de prueba manual",
       "tono":"Exploración","horario":"Viernes 20:00","estado":"abierta",
       "nivel_inicial":1,"jugadores_max":4}'
```

| Campo | Obligatorio | Valor válido | Si se manda mal |
|---|---|---|---|
| `nombre` | **Sí** | texto no vacío | `400 body.nombre: Field required` |
| `sistema` | **Sí** | `PF1e`, `D&D 5e`, o cualquier texto | `400 body.sistema: Field required` |
| `descripcion` | No | texto | — |
| `tono` | No | texto | — |
| `horario` | No | texto | — |
| `estado` | No | **`abierta`** o **`cerrada`** | `400 body.estado: Input should be 'abierta' or 'cerrada'` |
| `nivel_inicial` | No | entero ≥ 0 | `400 body.nivel_inicial: Input should be greater than or equal to 0` |
| `jugadores_max` | No | entero **> 0** | `400 body.jugadores_max: Input should be greater than 0` |

**Esperado:** `201` con la mesa creada, incluido su `id` **anotar ese id**, se usa en los
casos siguientes.

### 4.5 Editar mesa (actualización parcial)

| | |
|---|---|
| **URL** | `PUT http://localhost:8001/api/v1/mesas/<ID_ANOTADO>` |
| **Campo** | Header `Authorization` + body JSON |
| **Dato** | `{"descripcion":"Descripción editada"}` |
| **Esperado** | `200`. **Solo cambia lo enviado**; el resto queda igual |

> El método es **`PUT`**, no `PATCH`. Con `PATCH` la respuesta es `405`.

### 4.6 Editar mesa inexistente

| | |
|---|---|
| **URL** | `PUT http://localhost:8001/api/v1/mesas/99999` |
| **Campo** | body JSON |
| **Dato** | `{"descripcion":"x"}` |
| **Esperado** | `404 Mesa 99999 no encontrada` |

### 4.7 Borrar mesa

| | |
|---|---|
| **URL** | `DELETE http://localhost:8001/api/v1/mesas/<ID_ANOTADO>` |
| **Campo** | Header `Authorization` |
| **Dato** | — |
| **Esperado** | `204` con cuerpo **vacío**. Luego un `GET` a esa mesa da `404` |

### 4.8 Miembros de una mesa

| | |
|---|---|
| **URL** | `GET http://localhost:8001/api/v1/mesas/1/miembros` |
| **Campo** | Header `Authorization` |
| **Dato** | `Authorization: Bearer <ACCESS>` |
| **Esperado** | `200` con `{"mesa_id":1, "miembros":[...]}` |

---

## 5. Solicitud de unión (mesas-api, puerto 8001)

| | |
|---|---|
| **URL** | `POST http://localhost:8001/api/v1/mesas/1/solicitudes` |
| **Campo** | Header `Authorization` + header **`Idempotency-Key`** + body `{}` |
| **Dato** | `Idempotency-Key: unico-001` (cambiar en cada prueba) |
| **Esperado** | `201` con la solicitud creada |

```bash
curl -s -X POST http://localhost:8001/api/v1/mesas/1/solicitudes \
  -H "Authorization: Bearer $ACCESS" \
  -H "Idempotency-Key: union-$(date +%s)" \
  -H 'Content-Type: application/json' -d '{}'
```

| Variante | Dato | Esperado |
|---|---|---|
| Repetir **exactamente** la misma | mismo `Idempotency-Key` | `201` con el **mismo `id`** que la primera. No crea otra fila ni consume otra vacante |
| Mesa llena | mesa `2` con un usuario más | `409 Cupo agotado: no quedan vacantes` |
| Mesa inexistente | `99999` | `404 Mesa 99999 no encontrada` |
| Sin token | quitar el header | `401` |

### 5.1 Endpoint legacy (no usar para reservar cupos)

| | |
|---|---|
| **URL** | `POST http://localhost:8001/api/v1/mesas/1/solicitar` |
| **Campo** | Header `Authorization` + body `{}` |
| **Dato** | — |
| **Esperado** | `202 {"estado":"pendiente"}` |

> Devuelve `202` y **no** reserva la vacante de forma atómica. Para comprobar la reserva
> real hay que usar `/solicitudes`.

### 5.2 Carrera por la última vacante

Preparar una mesa con **una sola** vacante y disparar 3 solicitudes simultáneas con
usuarios y claves distintas:

```bash
# 1) Crear mesa de 1 jugador
MID=$(curl -s -X POST http://localhost:8001/api/v1/mesas \
  -H "Authorization: Bearer $GM" -H 'Content-Type: application/json' \
  -d '{"nombre":"Mesa Carrera","sistema":"D&D 5e","jugadores_max":1}' | jq -r .id)

# 2) Tres solicitudes al mismo tiempo
for i in 1 2 3; do
  T=$(curl -s -X POST http://localhost:8001/api/v1/auth/login -H 'Content-Type: application/json' \
      -d "{\"email\":\"jugador$i@tfinder.dev\",\"password\":\"DemoTFinder123!\"}" | jq -r .access_token)
  curl -s -o /dev/null -w "jugador$i -> %{http_code}\n" -X POST \
    "http://localhost:8001/api/v1/mesas/$MID/solicitudes" \
    -H "Authorization: Bearer $T" -H "Idempotency-Key: race-$i-$RANDOM" \
    -H 'Content-Type: application/json' -d '{}' &
done
wait
```

| **Esperado** | |
|---|---|
| Exactamente **1** respuesta `201` | un solo ganador |
| Las otras **2** en `409` | perdedores |
| `GET /api/v1/mesas/<MID>` → `jugadores_actuales: 1` de `1` | nunca se supera el máximo |
| 1 sola fila en `solicitudes_uniones` para esa mesa | en DBeaver, `mesas_db` → tabla `solicitudes_uniones` |

---

## 6. Matchmaking (mesas-api, puerto 8001)

| | |
|---|---|
| **URL** | `POST http://localhost:8001/api/v1/matchmaking/1/abrir` |
| **Campo** | Header `Authorization` |
| **Dato** | `Authorization: Bearer <token de GM>` |
| **Esperado** | `200` con `{"id":N,"mesa_id":1,"estado":"abierto",...}` |

Anotar el `id` devuelto para consultar el estado.

| | |
|---|---|
| **URL** | `GET http://localhost:8001/api/v1/matchmaking/<ID_ANOTADO>/estado` |
| **Campo** | Path: `mm_id` |
| **Dato** | el `id` del caso anterior |
| **Esperado** | `200` con `{"estado":"abierto","ttl_restante":120}` |

Casos de error:

| Variante | Dato | Esperado |
|---|---|---|
| Usuario normal intenta abrir | token de `jugador1` | `403 Rol insuficiente` |
| Sin token | — | `401` |
| Mesa inexistente | `99999` | `404 Mesa 99999 no encontrada` |

> El `ttl_restante` arranca en **120 segundos**. Pasado el TTL, el estado pasa a cerrado.
> Para verlo sin esperar, consultar de nuevo pasado un par de minutos.

---

## 7. QR de asistencia (mesas-api, puerto 8001)

Necesitás el **id de una sesión**. No hay endpoint para crearla: se crea por SQL.
Abrir DBeaver → base `mesas_db` → tabla `sesiones` → insertar una fila con `mesa_id = 1`,
o por terminal:

```bash
docker exec tfinder-postgres psql -U tfinder -d mesas_db \
  -c "INSERT INTO sesiones (mesa_id) VALUES (1) RETURNING id;"
```

### 7.1 Emitir QR

| | |
|---|---|
| **URL** | `POST http://localhost:8001/api/v1/sesiones/<ID_SESION>/qr` |
| **Campo** | Header `Authorization` |
| **Dato** | `Authorization: Bearer <token de GM>` |
| **Esperado** | `200` con `qr_data` (texto), `png_base64` (imagen) y `expira_en_seg` |

Guardar el `qr_data`:

```bash
QR=$(curl -s -X POST http://localhost:8001/api/v1/sesiones/$SID/qr \
  -H "Authorization: Bearer $GM" | jq -r .qr_data)
```

### 7.2 Validar QR (primer uso)

| | |
|---|---|
| **URL** | `POST http://localhost:8001/api/v1/sesiones/<ID_SESION>/qr/validar` |
| **Campo** | Body JSON: `usuario_id`, `qr_data` |
| **Dato** | `{"usuario_id":2,"qr_data":"<el qr_data del paso anterior>"}` |
| **Esperado** | `200 {"asistencia":"registrada"}` |

### 7.3 Casos de QR

| # | Variante | Dato | Esperado |
|---:|---|---|---|
| Q-01 | Primer uso | QR válido | `200 {"asistencia":"registrada"}` |
| Q-02 | **Reusar el mismo QR** | repetir Q-01 tal cual | `409 QR vencido o ya utilizado` |
| Q-03 | QR alterado | cambiar el último carácter del `qr_data` | `409 QR vencido o ya utilizado` |
| Q-04 | Otro usuario | mismo `qr_data`, `usuario_id` distinto | `409` |
| Q-05 | Sesión inexistente | `99999` en el path | `404 Sesión 99999 no encontrada` |
| Q-06 | Sin token | — | `401` |

> En la tabla `asistencias` de `mesas_db` debe haber **una sola fila** para esa sesión, aunque
> se hayan attempted los casos Q-01 a Q-04.

---

## 8. Builds (builds-api, puerto 8002)

Base: `http://localhost:8002/api/v1`

| # | URL | Método | Campo | Dato | Esperado |
|---:|---|---|---|---|---|
| B-01 | `/builds` | GET | — | — | `200` con 2 builds |
| B-02 | `/builds?mesa_id=1` | GET | Query `mesa_id` | `1` | `200` con los builds de esa mesa |
| B-03 | `/builds?mesa_id=99999` | GET | Query `mesa_id` | `99999` | `200` con `[]`. **No es error** |
| B-04 | `/builds/1` | GET | Path `build_id` | `1` | `200` con el detalle |
| B-05 | `/builds/99999` | GET | Path `build_id` | `99999` | `404 Build 99999 no encontrado` |
| B-06 | `/builds/abc` | GET | Path `build_id` | `abc` | `400 path.build_id: Input should be a valid integer, unable to parse string as an integer` |
| B-07 | `/tags` | GET | — | — | `200` con 13 tags |

### 8.1 Pedir el PDF de un build

| | |
|---|---|
| **URL** | `POST http://localhost:8002/api/v1/builds/1/pdf` |
| **Campo** | Header `Authorization` + body `{}` |
| **Dato** | `Authorization: Bearer <ACCESS>` |
| **Esperado** | `202 {"estado":"aceptado","documento_id":"<hex de 32>","detalle":"turno_enviado"}` |

**Anotar el `documento_id`.** El `202` **no** significa que el PDF esté listo: hay que
consultar el estado en el capítulo 11.

| Variante | Dato | Esperado |
|---|---|---|
| Sin token | quitar header | `401` |
| Build inexistente | `99999` | `404 Build 99999 no encontrado` |

---

## 9. Feed y wiki (feed-api, puerto 8003)

Base: `http://localhost:8003/api/v1`

### 9.1 Feed

`GET http://localhost:8003/api/v1/feed`

| # | Campo | Dato | Esperado |
|---:|---|---|---|
| F-01 | — | sin query | `200` con 3 publicaciones |
| F-02 | Query `tipo` | `post` | `200` solo las de tipo `post` |
| F-03 | Query `tipo` | `build` | `200` solo las de tipo `build` |
| F-04 | Query `tipo` | `wiki` | `200` solo las de tipo `wiki` |
| F-05 | Query `tipo` | `inventado` | `400`: el tipo no existe, no filtra en silencio |
| F-06 | Query `autor_id` | `3` | `200` solo las de ese autor |
| F-07 | Query `etiqueta` | `seed-demo-post` | `200` solo las de esa etiqueta |
| F-08 | Query `orden` | `votos` | `200` ordenadas de más a menos votos |
| F-09 | Query `orden` | `inventado` | `400 orden invalido: usar uno de antiguos, id, recientes, votos` |
| F-10 | Query `limit` | `2` | `200` con 2 elementos |
| F-11 | Query `offset` | `2` | `200` salteando los 2 primeros |
| F-12 | Query `limit` | `0` | `400 limit debe estar entre 1 y 100` |
| F-13 | Query `limit` | `500` | `400 limit debe estar entre 1 y 100` |
| F-14 | Query `offset` | `-1` | `400 offset no puede ser negativo` |
| F-15 | Query `autor_id` | `999` | `200` con `[]` |

Valores admitidos en `orden`: `id` (por defecto), `recientes`, `antiguos`, `votos`.

### 9.2 Wiki

`GET http://localhost:8003/api/v1/wiki`

| # | Campo | Dato | Esperado |
|---:|---|---|---|
| W-01 | — | sin query | `200` con `{"carpetas":[...],"paginas":[...],"total":2}` |
| W-02 | Query `mesa_id` | `demo-mesa` | `200` con las páginas de esa mesa |
| W-03 | Query `mesa_id` | `99999` | `200` con `{"carpetas":[],"paginas":[],"total":0}` |

### 9.3 PDF del diario de sesión

| | |
|---|---|
| **URL** | `POST http://localhost:8003/api/v1/mesas/1/sesiones/1/diario/pdf` |
| **Campo** | Header `Authorization` + body `{}` |
| **Dato** | `Authorization: Bearer <ACCESS>` |
| **Esperado** | `202` con `documento_id` |

| Variante | Dato | Esperado |
|---|---|---|
| Sin token | quitar header | `401` |

---

## 10. Notificaciones, SSE y email (notif-api, puerto 8004)

Base: `http://localhost:8004/api/v1`

### 10.1 Listar notificaciones

| | |
|---|---|
| **URL** | `GET http://localhost:8004/api/v1/notificaciones` |
| **Campo** | Header `Authorization` |
| **Dato** | `Authorization: Bearer <ACCESS>` |
| **Esperado** | `200` con los avisos del usuario **y los generales** (los que no tienen destinatario) |

> Solo se ven las del usuario del token. Un `jugador2` no ve los avisos de `jugador1`.

### 10.2 Filtrar no leídas

| | |
|---|---|
| **URL** | `GET http://localhost:8004/api/v1/notificaciones?solo_no_leidas=true` |
| **Campo** | Query `solo_no_leidas` |
| **Dato** | `true` |
| **Esperado** | `200` solo con las que tienen `leida: false` |

### 10.3 Marcar como leída

| | |
|---|---|
| **URL** | `PATCH http://localhost:8004/api/v1/notificaciones/<ID>/leida` |
| **Campo** | Header `Authorization` |
| **Dato** | `Authorization: Bearer <ACCESS>` y el `id` de una notificación **propia** |
| **Esperado** | `200` con la notificación ya con `leida: true` |

| Variante | Dato | Esperado |
|---|---|---|
| Sin token | quitar header | `401` |
| Aviso de **otro** usuario | token de `jugador2`, id de `jugador1` | `404 Notificación no encontrada`, y el aviso sigue sin leerse |
| Id inexistente | `99999` | `404` |

### 10.4 Stream en vivo (SSE)

| | |
|---|---|
| **URL** | `GET http://localhost:8004/api/v1/notificaciones/stream` |
| **Campo** | Header `Authorization` |
| **Dato** | `Authorization: Bearer <ACCESS>` |
| **Esperado** | Conexión abierta. Llega un `data:` por cada evento |

Probarlo de verdad — abrir el stream en una terminal y en otra disparar una unión:

```bash
# Terminal 1: queda esperando
curl -N http://localhost:8004/api/v1/notificaciones/stream -H "Authorization: Bearer $ACCESS"

# Terminal 2: dispara la notificación
curl -s -X POST http://localhost:8001/api/v1/mesas/1/solicitudes \
  -H "Authorization: Bearer $ACCESS" -H "Idempotency-Key: sse-$(date +%s)" \
  -H 'Content-Type: application/json' -d '{}'
```

**Esperado en la terminal 1:**

```text
data: {"id": 35, "titulo": "Solicitud aceptada", "detalle": "Tu solicitud para la mesa 9 fue aceptada", "entidad": "mesa", "enlace": {"label": "ver mesa", "to": "/mesas/9"}}
```

> El campo `enlace` viene con `label` (el texto del botón) y `to` (la ruta). Así lo consume
> el frontend.

### 10.5 Recuperar contraseña (envía email real)

| | |
|---|---|
| **URL** | `POST http://localhost:8004/api/v1/auth/recuperar` |
| **Campo** | Body JSON: `email` |
| **Dato** | `{"email":"jugador1@tfinder.dev"}` |
| **Esperado** | `202 {"ok":true}` y el correo aparece en `http://localhost:8025` |

| Variante | Dato | Esperado |
|---|---|---|
| Email **inexistente** | `{"email":"nadie@tfinder.dev"}` | `202 {"ok":true}` — **idéntico** al anterior, no revela si la cuenta existe |

### 10.6 Bandeja MailHog

| | |
|---|---|
| **URL** | `http://localhost:8025` |
| **Campo** | — |
| **Dato** | — |
| **Esperado** | Listado con `From: noreply@tfinder.local` y `To:` la dirección enviada |

---

## 11. PDFs asíncronos (notif-api, puerto 8004)

Después de pedir un PDF en los capítulos 8 u 9, con el `documento_id` anotado:

### 11.1 Consultar estado

| | |
|---|---|
| **URL** | `GET http://localhost:8004/api/v1/pdf/<DOCUMENTO_ID>/estado` |
| **Campo** | Path `documento_id` + Header `Authorization` |
| **Dato** | `Authorization: Bearer <ACCESS>` |
| **Esperado** | `200` con `{"documento_id":"...","tipo":"build","estado":"listo","fecha":"..."}` |

Poll hasta que aparezca `listo`:

```bash
for i in $(seq 1 10); do
  curl -s "http://localhost:8004/api/v1/pdf/$DOC/estado" -H "Authorization: Bearer $ADMIN"; echo
  sleep 1
done
```

| **Esperado** | |
|---|---|
| El estado progresa a `listo` | si se queda en `pendiente` o `procesando`, el worker está atascado |

### 11.2 Descargar

| | |
|---|---|
| **URL** | `GET http://localhost:8004/api/v1/pdf/<DOCUMENTO_ID>` |
| **Campo** | Header `Authorization` |
| **Dato** | `Authorization: Bearer <ACCESS>` |
| **Esperado** | `200`, header `content-type: application/pdf`, y el archivo abre |

```bash
curl -f -o documento.pdf "http://localhost:8004/api/v1/pdf/$DOC" -H "Authorization: Bearer $ADMIN"
file documento.pdf     # debe decir: PDF document, version 1.3, 1 page(s)
```

| Variante | Dato | Esperado |
|---|---|---|
| Sin token | quitar header | `401` |
| Id inexistente | 32 ceros | `404 Documento no disponible aún o no existe` |

---

## 12. Auditoría y operación (solo admin) — puerto 8004

### 12.1 Event log

| | |
|---|---|
| **URL** | `GET http://localhost:8004/api/v1/event-log` |
| **Campo** | Header `Authorization` + query opcional |
| **Dato** | `Authorization: Bearer <ADMIN>` |
| **Esperado** | `200` con el historial de eventos consumidos |

Filtros disponibles:

| Campo | Dato | Efecto |
|---|---|---|
| `correlation_id` | el id de una prueba anterior | Devuelve solo los eventos de esa operación |
| `entidad_tipo` | `mesa.aceptada` | Solo eventos de ese tipo |
| `entidad_id` | `8` | Solo eventos de esa entidad |

### 12.2 Trazabilidad de punta a punta (prueba recomendada)

Un solo `correlation_id` seguido a través de todo el sistema:

```bash
CID="mi-prueba-$(date +%s)"

# 1) Originador: una unión en mesas-api, con el correlation id en el header
curl -s -X POST http://localhost:8001/api/v1/mesas/1/solicitudes \
  -H "Authorization: Bearer $ACCESS" \
  -H "Idempotency-Key: traza-$(date +%s)" \
  -H "X-Correlation-Id: $CID" \
  -H 'Content-Type: application/json' -d '{}'

sleep 4

# 2) Rastro en el event log (solo admin)
curl -s "http://localhost:8004/api/v1/event-log?correlation_id=$CID" -H "Authorization: Bearer $ADMIN" | jq
```

| **Esperado** | |
|---|---|
| `200` con el evento `mesa.aceptada` | el mensaje cruzó RabbitMQ y fue consumido |
| `correlationId` idéntico al enviado | la correlación se preserva de punta a punta |
| El `metadata` trae `{"mesa_id": N}` | el payload del evento se conservó |
| Apareció una notificación nueva para los usuarios de la mesa | el evento produjo un efecto real |

### 12.3 Bandeja de emails

| | |
|---|---|
| **URL** | `GET http://localhost:8004/api/v1/emails` |
| **Campo** | Header `Authorization` + query `limite` opcional |
| **Dato** | `Authorization: Bearer <ADMIN>` |
| **Esperado** | `200` con el registro de envíos, su estado (`enviado` / `fallido`) y el error si lo hubo |

Reintentar un envío fallido:

| | |
|---|---|
| **URL** | `POST http://localhost:8004/api/v1/emails/<EMAIL_ID>/reintentar` |
| **Campo** | Header `Authorization` |
| **Dato** | `Authorization: Bearer <ADMIN>` |
| **Esperado** | `200`. Con MailHog parado primero, el estado queda `fallido` |

### 12.4 Dead letter queue (DLQ)

| | |
|---|---|
| **URL** | `GET http://localhost:8004/api/v1/dlq` |
| **Campo** | Header `Authorization` + query `limite` opcional |
| **Dato** | `Authorization: Bearer <ADMIN>` |
| **Esperado** | `200` con los mensajes que fallaron tras 3 reintentos |

Anotar el `id` del primer mensaje para las dos acciones siguientes.

| Acción | URL | Método | Campo | Dato | Esperado |
|---|---|---|---|---|---|
| Reintentar | `/api/v1/dlq/<ID_ANOTADO>/reintentar` | POST | Header `Authorization` | token de `admin` | `200 {"ok":true,"id":N}`. Desaparece del listado |
| Descartar | `/api/v1/dlq/<ID_ANOTADO>` | DELETE | Header `Authorization` | token de `admin` | `200 {"ok":true}`. Desaparece del listado |
| Descartar dos veces | mismo `DELETE` repetido | DELETE | Header `Authorization` | token de `admin` | `404 Mensaje no encontrado en DLQ` |
| Con rol no admin | `/api/v1/dlq` | GET | Header `Authorization` | token de `usuario` | `403 Rol insuficiente` |

### 12.5 Colas y exchanges en RabbitMQ

Abrir `http://localhost:15673` → pestaña **Queues and Streams**.

| Qué | Nombre esperado | Con consumidores |
|---|---|---:|
| Exchange de eventos | `tfinder.events` (topic) | — |
| Exchange de dead letter | `tfinder.dlx` (topic) | — |
| Cola de mesas | `notif.mesa` | 1 |
| Cola de sesiones | `notif.sesion` | 1 |
| Cola de PDFs | `doc.pdf` | 1 |
| Cola de errores | `dlq.general` | 0 (normal) |

Bindings esperados:

| Desde | Hacia | Routing key |
|---|---|---|
| `tfinder.events` | `notif.mesa` | `mesa.*` |
| `tfinder.events` | `notif.sesion` | `sesion.*` |
| `tfinder.events` | `doc.pdf` | `doc.pdf.*` |
| `tfinder.dlx` | `dlq.general` | `#` |

> Las 4 colas de consumo tienen un consumidor porque el `notif-api` corre en Docker. Si
> `Consumers` está en 0, el worker no arrancó.

---

## 13. Frontend (http://localhost:5173)

### 13.1 Rutas que deben cargar sin error "Próximamente"

| Ruta | Qué tiene que mostrar |
|---|---|
| `/` | Landing con botón **Explorar mesas** |
| `/mesas` | Listado de las 3 mesas demo |
| `/login` | Formulario de email y contraseña |
| `/registro` | Formulario de alta |
| `/recuperar` | Formulario de recuperación |
| `/matchmaking` | Listado de llamados |
| `/notificaciones` | Avisos del usuario + campana con contador |
| `/mesas/nueva` | Formulario de creación de mesa |

### 13.2 Rutas que deben mostrar "Próximamente"

| Ruta |
|---|
| `/dashboard`, `/perfil`, `/campanas`, `/gestion`, `/calendario`, `/votaciones`, `/jugadores`, `/directorio` |

### 13.3 Casos defrontend

| # | Pasos | Esperado |
|---:|---|---|
| F-01 | Abrir `/` → **Explorar mesas** | Navega a `/mesas` |
| F-02 | En `/mesas`, buscar por nombre | Filtra la lista sin llamar a la API |
| F-03 | En `/mesas`, filtrar por sistema y disponibilidad | Filtra la lista |
| F-04 | Buscar algo inexistente | Estado vacío, no pantalla de error |
| F-05 | Abrir `/mesas/99999` | Estado de error controlado, no pantalla en blanco |
| F-06 | Abrir el detalle de una mesa **sin sesión** y pulsar unirse | Redirige a `/login?redirect=/mesas/<id>` |
| F-07 | Iniciar sesión con `jugador1@tfinder.dev` / `DemoTFinder123!` | Vuelve a la mesa que se quería |
| F-08 | Recargar el navegador con sesión activa | La sesión sigue viva (refresh token) |
| F-09 | Cerrar sesión y volver a una ruta protegida | Vuelve al login |
| F-10 | Registrarse con un email nuevo | `201`; la cuenta nace con rol `usuario` aunque mandes `rol: admin` |
| F-11 | Registrarse con un email ya existente | Error, **sin** sobrescribir la cuenta original |
| F-12 | Campana del header con avisos sin leer | Muestra el contador y actualiza solo |
| F-13 | Con `notif-api` apagado | La campana se atenúa y el contador queda en 0 |

### 13.4 Con DBeaver abierto en paralelo

Para ver qué escribe el frontend en cada momento:

1. Conectar DBeaver a `mesas_db`.
2. Refrescar la tabla `mesas` antes y después de cada acción del frontend.
3. Lo mismo con `notif_db` → `notificaciones` y `event_log`.

---

## 14. Comprobaciones por base de datos

Con DBeaver o por terminal. Sirven para confirmar que lo que se ve en pantalla
realmente se persistió.

```bash
# Mesas y usuarios
docker exec tfinder-postgres psql -U tfinder -d mesas_db \
  -c "SELECT id,nombre,estado,jugadores_actuales,jugadores_max FROM mesas ORDER BY id;"
docker exec tfinder-postgres psql -U tfinder -d mesas_db \
  -c "SELECT id,email,rol FROM usuarios ORDER BY id;"

# Solicitudes de unión (la clave de idempotencia debe ser única)
docker exec tfinder-postgres psql -U tfinder -d mesas_db \
  -c "SELECT id,mesa_id,usuario_id,estado,idem_key FROM solicitudes_uniones ORDER BY id;"

# Asistencias (una fila por QR validado)
docker exec tfinder-postgres psql -U tfinder -d mesas_db \
  -c "SELECT id,sesion_id,usuario_id FROM asistencias ORDER BY id;"

# Matchmaking
docker exec tfinder-postgres psql -U tfinder -d mesas_db \
  -c "SELECT id,mesa_id,estado,llamada_abierta_at FROM matchmaking ORDER BY id;"

# Builds, feed, notificaciones
docker exec tfinder-postgres psql -U tfinder -d builds_db -c "SELECT id,nombre,nivel FROM builds;"
docker exec tfinder-postgres psql -U tfinder -d feed_db -c "SELECT id,tipo,titulo,votos FROM publicaciones;"
docker exec tfinder-postgres psql -U tfinder -d notif_db -c "SELECT id,usuario_id,mensaje,leida FROM notificaciones;"
docker exec tfinder-postgres psql -U tfinder -d notif_db -c "SELECT id,entidad_tipo,correlation_id FROM event_log;"
docker exec tfinder-postgres psql -U tfinder -d notif_db -c "SELECT id,cola,error FROM mensaje_dlq;"
```

---

## 15. Health checks de todos los servicios

| Puerto | Servicio | `/health` | `/live` | `/ready` |
|---:|---|---|---|---|
| 8001 | mesas-api | `{"status":"ok","servicio":"mesas-api"}` | `{"estado":"vivo"}` | `{"estado":"listo","dependencias":{...}}` |
| 8002 | builds-api | `{"status":"ok","servicio":"builds-api"}` | `{"estado":"vivo"}` | idem |
| 8003 | feed-api | `{"status":"ok","servicio":"feed-api"}` | `{"estado":"vivo"}` | idem |
| 8004 | notif-api | `{"status":"ok","servicio":"notif-api"}` | `{"estado":"vivo"}` | idem |

```bash
for port in 8001 8002 8003 8004; do
  echo "--- $port"
  curl -s "http://localhost:$port/health"; echo
  curl -s "http://localhost:$port/live"; echo
  curl -s "http://localhost:$port/ready"; echo
done
```

| Campo | Significado |
|---|---|
| `/health` | El proceso responde. No consulta nada |
| `/live` | El proceso está vivo. Para reiniciar si falla |
| `/ready` | **Todas las dependencias** están accesibles |

| **Esperado en `/ready`** | |
|---|---|
| `estado: "listo"` con las 3 dependencias en `true` | todo bien |
| `estado: "degradado"` o `503` con alguna en `false` | falta PostgreSQL, Redis o RabbitMQ |

Comprobar el `/ready` degradado (requiere autorización, reinicia el contenedor al terminar):

```bash
docker pause tfinder-redis
curl -i http://localhost:8001/ready        # esperado: 503, redis: false
docker unpause tfinder-redis
curl -i http://localhost:8001/ready        # esperado: 200, listo otra vez
```

---

## 16. Pruebas automatizadas

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt -r requirements-dev.txt

venv/bin/ruff check .                # lint
venv/bin/pytest -m unit -q          # 50 tests unitarios
venv/bin/pytest -m integration -q   # 80 tests de integración

cd tfinder-vue
npm ci
npm run lint
npm run type-check
npm run test:unit -- --run         # 15 tests
npm run test:integration -- --run  # 7 tests
npm run build
```

| Suite | Requiere |
|---|---|
| `-m unit` | nada externo |
| `-m integration` | PostgreSQL, Redis y RabbitMQ levantados, y las 4 bases `*_db_test` |

Los tests de integración usan un **vhost de RabbitMQ propio** (`tfinder_test`), así que
**no tocan** las colas del ambiente de desarrollo. Para comprobarlo:

```bash
docker exec tfinder-rabbitmq rabbitmqctl list_queues -p / name messages
# dlq.general debe quedar en 0 después de correr la suite
```

---

## 17. Checklist final

Antes de dar por probado el sistema:

- [ ] Los 4 servicios responden `200` en `/health`, `/live` y `/ready`
- [ ] Login con las 6 cuentas demo
- [ ] Registro crea una cuenta usable y **nunca** con rol privilegiado
- [ ] Crear, editar y borrar una mesa
- [ ] Unirse a una mesa devuelve `201` y **no** supera el máximo de jugadores
- [ ] Repetir la misma `Idempotency-Key` no duplica nada
- [ ] La carrera por la última vacante deja un solo ganador
- [ ] Solo un GM puede abrir un llamado; el estado muestra el TTL
- [ ] El QR valida una vez y da `409` en el reuso
- [ ] El PDF pasa de `202` a `listo` y descarga un archivo válido
- [ ] Las notificaciones se listan, se filtran y se marcan como leídas
- [ ] El SSE entrega el evento en vivo
- [ ] La recuperación de contraseña llega a MailHog
- [ ] El `event-log` encuentra el evento por `correlation_id`
- [ ] La DLQ lista, reintenta y descarta
- [ ] RabbitMQ tiene los 2 exchanges, las 4 colas y los 4 bindings
- [ ] Los errores de los 4 servicios usan el mismo envelope `{"error":{...}}`
- [ ] Ningún endpoint protegido responde sin `401` o `403`
- [ ] La suite automatizada pasa entera

---

## 18. Resumen de credenciales

| Recurso | Dato |
|---|---|
| PostgreSQL | `tfinder` / `tfinder` en `localhost:5432` |
| RabbitMQ | `tfinder` / `tfinder` en `localhost:5673` (panel en `15673`) |
| Redis | sin password en `localhost:6390` |
| MailHog | sin password, panel en `localhost:8025` |
| Cuentas demo | `admin@`, `gm@`, `jugador1..3@`, `email_svc@tfinder.dev` con `DemoTFinder123!` |
| JWT | `JWT_SECRET=dev-secret`, expiración 1440 min (24 h) |

> Todo esto es **solo para desarrollo local**. Ningún valor de esta tabla debe aparecer en
> un ambiente de entrega.
