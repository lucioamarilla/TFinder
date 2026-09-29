---
title: "TFinder AE2 — Demostración de la aplicación"
subtitle: "Recorrido pantalla por pantalla: rutas, datos a ingresar, llamadas a la API y respuestas verificadas"
date: "Verificado contra el stack en vivo el 2026-09-29"
lang: es-AR
---

# 0. Qué se demuestra y qué no

Este documento describe **únicamente lo que funciona**. Cada paso fue ejecutado contra el
stack levantado y la respuesta real está copiada en el texto.

## 0.1 La cifra que importa

La aplicación declara **45 rutas** en el router. De ellas:

| Grupo | Cantidad | Estado |
|---|---:|---|
| Rutas sin *feature flag* (siempre alcanzables) | 7 | 6 funcionan |
| Rutas con flag encendida | 7 | 5 funcionan, 1 frágil, 2 rotas |
| Rutas con flag apagada (caen en "Próximamente") | 31 | bloqueadas por diseño |
| **Total** | **45** | |

**La demostración real son 11 pantallas, no 43.** No es una limitación del trabajo: es el
resultado de haber puesto un interruptor de funcionalidad delante de cada módulo, y de haber
conectado a la API real solamente los caminos que la usan.

## 0.2 Inventario de las 45 rutas

| # | Ruta | Flag | Veredicto |
|--:|---|---|---|
| 1 | `/` | — | correcta, pública |
| 2 | `/mesas` | — | **API real** |
| 3 | `/mesas/:id` | — | **API real** + unirse |
| 4 | `/login` | — | **API real** |
| 5 | `/registro` | — | **API real** |
| 6 | `/recuperar` | `recuperacion` | **API real** |
| 7 | `/proximamente/:feature` | — | es la demo del flag |
| 8 | `/:pathMatch(.*)*` | — | 404 |
| 9 | `/notificaciones` | `notificaciones` | **API real** |
| 10 | `/matchmaking` | `matchmaking` | **API real** + polling |
| 11 | `/encuentros` | `encuentros` | cliente puro, sin API |
| 12 | `/mesas/nueva` | `crearMesa` | **ROTA: 400 al guardar** (Anexo A.1) |
| 13 | `/mesas/:id/editar` | `editarMesa` | **ROTA: 400 al guardar** (Anexo A.1) |
| 14 | `/mesas/:id/sesiones/:sesionId/qr` | `qr` | frágil: se demuestra por API (7.1) |
| 15-45 | dashboard, mis-mesas, gestion, wiki x4, calendario, sesiones, diario, jugadores, mesa-builds, builds x5, feed x2, perfil, usuario-detalle, tags, admin x10 | apagadas | "Proximamente" |

Recuento verificado sobre el router: **45 rutas = 7 sin flag + 7 con flag encendida + 31 con flag
apagada**.

## 0.3 La honestidad como estrategia

Tres cosas que conviene decir **antes** de que el jurado las encuentre:

1. **12 de los 14 servicios del frontend leen JSON local, no la API.** Solo `mesas.js` y
   `notificaciones.js` hacen peticiones reales. Las pantallas bloqueadas por flag son, en su
   mayoria, maquetas terminadas que esperan conexion.
2. **Dos pantallas estan rotas contra el backend.** El formulario de mesa manda un cuerpo
   que el servidor rechaza. Esta documentado en el Anexo A con el error exacto.
3. **Las 13 flags apagadas son un requisito, no una falla.** Demostrarlas es parte del
   guion (seccion 4).

---

# 1. Antes de empezar

## 1.1 Estado inicial limpio

El volumen de Postgres persiste entre corridas. Para que los datos sean los del *seed* y no
los de pruebas anteriores:

```bash
docker compose down -v
docker compose up -d --build
```

> Sin el `-v` se arrastran mesas, notificaciones y usuarios de corridas previas. En una
> corrida sin limpiar se llegaron a contar **47 notificaciones** acumuladas, lo que vuelve
> la pantalla del centro de avisos inutilizable como demostracion.

## 1.2 Verificacion de arranque

```bash
for p in 8001 8002 8003 8004; do
  printf "%s -> " $p
  curl -s -w " [HTTP=%{http_code}]\n" http://127.0.0.1:$p/ready
done
```

Respuesta real de los cuatro servicios:

```json
{"estado":"listo","dependencias":{"postgres":true,"redis":true,"rabbitmq":true}}
```

## 1.3 Cuentas

Todas con contrasena `DemoTFinder123!` (definida en `DEMO_SEED_PASSWORD`).

| Email | Rol (id) | Para que | Es admin en la UI? |
|---|---|---|---|
| `admin@tfinder.dev` | `admin` (1) | Ver las 10 pantallas `/admin/*` | **Si** |
| `gm@tfinder.dev` | `gm` (2) | Gestionar, emitir QR, abrir llamado | **No** |
| `jugador1@tfinder.dev` | `usuario` (3) | Unirse a mesas, ver avisos | No |
| `jugador2@tfinder.dev` | `usuario` (4) | Segundo jugador | No |
| `jugador3@tfinder.dev` | `usuario` (5) | Completar la mesa casi llena | No |
| `email_svc@tfinder.dev` | `usuario` (6) | Cuenta de servicio interna | No |

> **Trampa de roles.** El frontend solo distingue tres roles: `guest`, `auth` y `admin`. La
> funcion que mapea el rol del backend es: si es exactamente `admin` produce `admin`;
> cualquier otro rol con sesion produce `auth`. Por eso **`gm@` no entra a `/admin/*`**: el
> guard lo devuelve a `/mesas`. Para ver las consolas hay que entrar con
> `admin@tfinder.dev`.

## 1.4 Datos de mesa que siempre existen

| id | Nombre | Sistema | Estado | Ocupacion | Nivel |
|--:|---|---|---|:--:|---:|
| 1 | Mesa Demo Abierta | PF1e | `abierta` | 2/4 | 1 |
| 2 | Mesa Demo Casi Llena | PF1e | `abierta` | **3/4** | 3 |
| 3 | Mesa Demo Cerrada | D&D 5e | `cerrada` | 0/6 | 5 |

Sesiones: `id=1` (mesa 1, `abierta`) y `id=2` (mesa 3, `cerrada`).

La **mesa 2 con 3/4** es la pieza clave: tiene una sola vacante, y sirve para demostrar la
carrera por el ultimo cupo (seccion 3.3).

## 1.5 Paneles de control

| Panel | Direccion | Credenciales |
|---|---|---|
| RabbitMQ | <http://localhost:15673> | `tfinder` / `tfinder` |
| MailHog | <http://localhost:8025> | — |
| Swagger mesas-api | <http://localhost:8001/docs> | — |
| Swagger builds-api | <http://localhost:8002/docs> | — |
| Swagger feed-api | <http://localhost:8003/docs> | — |
| Swagger notif-api | <http://localhost:8004/docs> | — |

Ojo con los puertos: **Redis es 6390** (no 6379) y **AMQP es 5673** (no 5672), porque se
publicaron en puertos alternativos del host.

---

# 2. Recorrido sin sesion — 5 pantallas

## 2.1 `/` — Landing

**Que mostrar.** La portada publica. En el buscador escribir `PF1e` y pulsar Enter: la
aplicacion navega a `/mesas?q=PF1e`, lo que demuestra que la busqueda de la landing y la
lista estan conectadas por parametro de URL.

**Que pasa por detras.** Ninguna llamada a la API. La landing es estatica.

## 2.2 `/mesas` — Catalogo (API real)

**Datos a ingresar.** En la columna lateral:

| Filtro | Valores disponibles | Efecto |
|---|---|---|
| Busqueda | texto libre | filtra por nombre, sistema, descripcion |
| Sistema | PF1e / PF2e / D&D 3.5 / Starfinder | filtra por sistema |
| Modalidad | Online / Presencial / Mixta | filtra |
| Disponibilidad | **Con vacantes** / Completas | filtra por `jugadores_actuales < jugadores_max` |

El boton **Aplicar** dispara la llamada; **Limpiar** restablece.

**Llamada que dispara:**

```
GET /mesas/api/v1/mesas
```

que en el backend es:

```
GET http://mesas-api:8001/api/v1/mesas
```

**Respuesta real:**

```json
[
  {"id": 1, "nombre": "Mesa Demo Abierta", "sistema": "PF1e",
   "descripcion": "Campaña abierta para explorar el flujo principal.",
   "tono": "Exploración y", "horario": "Viernes 20:00",
   "estado": "abierta", "nivel_inicial": 1,
   "jugadores_actuales": 2, "jugadores_max": 4},
  {"id": 2, "nombre": "Mesa Demo Casi Llena", "sistema": "PF1e",
   "estado": "abierta", "nivel_inicial": 3,
   "jugadores_actuales": 3, "jugadores_max": 4},
  {"id": 3, "nombre": "Mesa Demo Cerrada", "sistema": "D&D 5e",
   "estado": "cerrada", "jugadores_actuales": 0, "jugadores_max": 6}
]
```

**Que observar en pantalla.** En la esquina aparece una etiqueta verde de **cache** con el
tiempo de respuesta medido. Es la primera prueba de que hay un cache de Redis detras.

**Que NO es evidencia.** Ese numero mide cuanto tardo el navegador, no si vino de Redis. La
prueba real del cache esta en el documento de infraestructura: la segunda llamada no vuelve
a tocar Postgres.

## 2.3 `/mesas/1` — Detalle y unirse (API real)

**Tabs.** "Resumen de la Cronica" y "Miembros de la Partida".

**Accion principal.** Boton **"Quiero unirme"**. La maquina de estados del boton es:

```
inactivo  --enviar-->  enviando  --201-->  solicitada
                                       --409-->  agotada
                                       --err-->  error  --Reintentar-->  inactivo
```

Si no hay sesion, el boton redirige a `/login?redirect=/mesas/1` y al volver a entrar
continua exactamente donde estaba.

**Llamada que dispara:**

```
POST /mesas/api/v1/mesas/1/solicitudes
Authorization: Bearer <token>
Idempotency-Key: tfinder-idem:solicitud:1:3
```

**Respuesta real (201):**

```json
{"id":15,"mesa_id":1,"usuario_id":3,"estado":"aceptada",
 "idem_key":"probe-join-1","fecha":"2026-09-29T16:49:57.447022+00:00"}
```

> **Plural, no singular.** El endpoint que reserva cupo es `/solicitudes` (termino en *s*).
> Existe tambien `/mesas/{id}/solicitar`, en singular, que devuelve `202` y **no escribe
> nada en la base**: solo publica un evento. Es un endpoint heredado, y el contador de
> jugadores unicamente se mueve por el plural. Es la confusion mas probable si el jurado
> lo dispara por error.

**Que observar.** Al volver a la lista, la ocupacion paso de `2/4` a `3/4`.

## 2.4 `/registro` y `/login` — Cuentas (API real)

**Datos a ingresar** en el registro:

| Campo | Regla de validacion | Mensaje si falla |
|---|---|---|
| Nombre | obligatorio | — |
| Email | formato `x@y.z` | — |
| Contrasena | **minimo 8 caracteres** | feedback en vivo |
| Confirmacion | debe coincidir | feedback en vivo |
| Casilla de normas | debe estar marcada | — |

**Llamada:** `POST /mesas/api/v1/auth/register`

**Restriccion importante.** El registro publico **siempre crea rol `usuario`**, aunque el
cuerpo mande `"rol": "gm"`. Verificado: un intento de escalar por el registro no genera una
cuenta privilegiada, ni siquiera si el rol se incluye explicitamente en el JSON.

**Que observar.** El token que devuelve el login es **el mismo valido en los cuatro
servicios**: es un JWT firmado con una clave compartida, y cada servicio valida contra la
misma clave y contra la misma sesion en Redis. No hay que volver a autenticarse al cambiar
de microservicio.

## 2.5 `/recuperar` — Recuperacion (API real)

**Datos a ingresar.** Solo el email.

**Llamada:** `POST /notif/api/v1/auth/recuperar` responde **202** con `{"ok": true}`
**siempre**, exista o no la cuenta. Es deliberado: responder distinto segun el email exista
permitiria enumerar las cuentas registradas.

**Que observar.** El correo llega a **MailHog** (panel en el 8025), y queda registrado en
la bandeja de salida.

---

# 3. Recorrido con sesion — 4 pantallas

Entrar con `gm@tfinder.dev` / `DemoTFinder123!`.

## 3.1 `/notificaciones` — Centro de avisos (API real)

**Acciones.** Los cuatro filtros de grupo (`todas` / `mesas` / `social` / `sesiones`) con
contador, el boton **Marcar todas como leidas**, y hacer clic en un aviso para abrir su
enlace.

**Llamadas:**

```
GET   /notif/api/v1/notificaciones[?solo_no_leidas=true]
PATCH /notif/api/v1/notificaciones/{id}/leida
```

**Respuesta real** (recortada):

```json
[
  {"id": 103, "grupo": "mesas", "icono": "solicitud",
   "leida": false, "mensaje": "Solicitud aceptada"},
  {"id": 101, "grupo": "mesas", "leida": true,
   "mensaje": "Sesion confirmada"}
]
```

**Alcance.** Cada usuario ve **las suyas mas las globales** (`usuario_id IS NULL`). No se
puede marcar como leida la notificacion de otro: devuelve `404`.

**Que observar.** La campana de la barra de navegacion se actualiza sola cada **5 segundos**.
Es *polling*, no tiempo real.

## 3.2 `/matchmaking` — Llamado con ventana de 120 s (API real)

**Acciones segun rol:**

| Accion | Quien la ve |
|---|---|
| **Abrir llamado** | solo `gm` |
| **Refrescar catalogo** | solo `gm` |
| **Anotarse al llamado** | cualquiera, si hay vacante y el llamado esta abierto |

**Secuencia de llamadas:**

```
POST /mesas/api/v1/matchmaking/{mesa_id}/abrir          -> 200, devuelve matchmaking_id
GET  /mesas/api/v1/matchmaking/{matchmaking_id}/estado   -> se consulta cada 2000 ms
POST /mesas/api/v1/mesas/{id}/solicitudes                -> anotarse
```

**Respuesta real de `abrir`:**

```json
{"id":2,"mesa_id":1,"estado":"abierto",
 "llamada_abierta_at":"2026-09-29T16:50:09.484707+00:00",
 "matchmaking_id":2,"expira_en":120}
```

> **Asimetria de la API — trampa real.** El `abrir` recibe el **`mesa_id`**, pero el
> `estado` recibe el **`matchmaking_id`**, que son numeros distintos. En el ejemplo: se
> abrio sobre la mesa 1 y devolvio `matchmaking_id: 2`.
>
> Consultar `/matchmaking/1/estado` devuelve `{"estado":"cerrado","ttl_restante":0}`, que
> es la fila de matchmaking de otra mesa, no un error. Con el id correcto:
>
> ```json
> {"estado":"abierto","ttl_restante":114}
> ```

**Que observar.** La cuenta regresiva que baja de 120. Al llegar a 0 el llamado se cierra y
el boton deja de responder.

## 3.3 La carrera por la ultima vacante

Este es el momento mas fuerte de la defensa. **Preparacion:** la mesa 2 esta en 3/4. Se
registran dos cuentas nuevas para tener dos identidades que compiten.

```bash
# Identidad A
A=$(curl -s -X POST http://127.0.0.1:8001/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"a@tfinder.dev","password":"DemoTFinder123!","nombre":"A"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# Identidad B
B=$(curl -s -X POST http://127.0.0.1:8001/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"b@tfinder.dev","password":"DemoTFinder123!","nombre":"B"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# La carrera, en paralelo
curl -s -o /dev/null -w "A: %{http_code}\n" -X POST \
  http://127.0.0.1:8001/api/v1/mesas/2/solicitudes \
  -H "Authorization: Bearer $A" -H 'Idempotency-Key: keyA' \
  -H 'Content-Type: application/json' -d '{"rol":"jugador"}' &

curl -s -w "\nB: %{http_code}\n" -X POST \
  http://127.0.0.1:8001/api/v1/mesas/2/solicitudes \
  -H "Authorization: Bearer $B" -H 'Idempotency-Key: keyB' \
  -H 'Content-Type: application/json' -d '{"rol":"jugador"}'
```

**Resultado real obtenido en la verificacion:**

```json
{"id":16,"mesa_id":2,"usuario_id":10,"estado":"aceptada","idem_key":"probeA-1"}
 HTTP=201
```

```json
{"error":{"codigo":409,"mensaje":"Cupo agotado: no quedan vacantes"}}
 HTTP=409
```

Y la mesa quedo en **4/4**, no en 5/4.

**Que esta pasando por dentro.** Dos barreras, en este orden:

1. **Redis** — `SET reserva:vacante:2 NX EX 60`. Solo una peticion puede pasar; las demas
   reciben `409` de inmediato.
2. **Postgres** — un `UPDATE ... WHERE jugadores_actuales < jugadores_max`. Aunque Redis
   falle, esta condicion en la base impide el sobrecupo.

Cada barrera falla con un `409` distinto, lo que permite saber en cual se cayo.

**Prueba de idempotencia.** Repetir la misma llamada con la **misma** `Idempotency-Key`
devuelve **la misma fila, no una nueva**:

```json
{"id":15, "idem_key":"probe-join-1"}   HTTP=201   <-- misma fila, mismo id
```

Y el contador de la mesa **no se movio** de 3 a 4. La clave vive en Redis 24 horas.

## 3.4 `/encuentros` — Generador de encuentros (cliente puro)

**Datos a ingresar:**

| Campo | Valores |
|---|---|
| Nivel del grupo | 3 / 4 / 5 / 6 |
| Dificultad | Trivial / Media / Desafiante / Epica |
| Entorno | Ruinas subterraneas / Ciudad / Bosque / Pantano |

**Accion.** Pulsar **Lanzar encuentro**.

**Que pasa por detras.** **Nada.** No hay llamada a la API. Todo el calculo ocurre en el
navegador: el modificador de dificultad, el calculo de XP objetivo, el resultado del dado y
el botin.

> **Decilo explicitamente.** Esta pantalla es un calculo en el cliente, no una funcionalidad
> del backend. Si el jurado pregunta si esta conectada a la base, la respuesta es que no, y
> que es una herramienta de apoyo para el grupo. Presentarla como "una mas del sistema" seria
> inexacto.

---

# 4. El sistema de feature flags

Las 13 flags apagadas no son una falla pendiente: son un mecanismo implementado, y
demostrarlo es parte del guion.

## 4.1 La demostracion

1. Entrar con `admin@tfinder.dev`.
2. Ir a `/admin/estadisticas` **escribiendo la URL**.
3. La pantalla que aparece es **"Proximamente"**, con el nombre de la funcion.
4. Abrir `tfinder-vue/src/config/features.js` y mostrar la linea:

```javascript
admin: { label: 'Administración', available: false },
```

5. Volver a la URL: misma respuesta.

## 4.2 Las dos capas de bloqueo

El guard evalua **en este orden**, y el orden es deliberado:

```
1. La feature esta apagada?  ->  /proximamente/:feature    (gana siempre)
2. El rol tiene permiso?     ->  /login?redirect=...  o  /mesas
```

Que la feature se evalue **primero** implica que ni siquiera un administrador ve una
pantalla a medio construir.

## 4.3 El estado de las 20 flags

| Encendidas (7) | Apagadas (13) |
|---|---|
| `crearMesa`, `editarMesa`, `qr`, `matchmaking`, `notificaciones`, `encuentros`, `recuperacion` | `dashboard`, `perfil`, `misMesas`, `gestionMesa`, `wiki`, `calendario`, `sesiones`, `jugadores`, `builds`, `feed`, `directorio`, `tags`, `admin` |

> **No las actives antes de la defensa.** Encender las 13 expone las dos pantallas rotas
> (Anexo A.1) y muestra muchas pantallas puramente maqueta. Amplia la superficie de riesgo
> sin aportar funcionalidad real.

---

# 5. Orden de una sentada — 10 minutos

| # | Min | Accion | Ruta | Que prueba |
|--:|--:|---|---|---|
| 1 | 0:00 | Arranque, `/ready` x4 | — | Los 3 servicios de infraestructura |
| 2 | 0:30 | RabbitMQ abierto en otra pestana | — | 4 colas, 3 con consumidor |
| 3 | 1:00 | `/mesas` + filtro "Con vacantes" | `/mesas` | Listado real + cache |
| 4 | 2:00 | Detalle de la mesa 2, "3/4" | `/mesas/2` | ocupacion vs maximo |
| 5 | 2:30 | Unirse con `jugador1` | `/mesas/2` | `POST /solicitudes` -> 201 |
| 6 | 3:30 | Volver atras: ahora "4/4" | `/mesas/2` | El contador se movio |
| 7 | 4:00 | `/notificaciones` | `/notificaciones` | Aviso generado por el evento |
| 8 | 5:00 | Login como `gm` | `/login` | Token unico para los 4 servicios |
| 9 | 5:30 | `/matchmaking` -> Abrir llamado | `/matchmaking` | `POST /abrir` -> ventana de 120 s |
| 10 | 6:30 | Ver la cuenta regresiva | `/matchmaking` | Polling cada 2 s, TTL en Redis |
| 11 | 7:00 | `/encuentros` -> Lanzar | `/encuentros` | Calculo en cliente (declararlo) |
| 12 | 7:30 | `/admin/estadisticas` | `/admin/*` | "Proximamente" — el flag system |
| 13 | 8:00 | `/recuperar` con un email | `/recuperar` | 202 + correo en MailHog |
| 14 | 9:00 | Terminal: correlacion | — | Un `X-Correlation-Id` de punta a punta |

> Los ultimos 4 minutos son los del documento **DEMO-INFRAESTRUCTURA**. Si el tiempo
> aprieta, se cortan los pasos 11 a 13 y se queda solo con el paso 14, que es el mas fuerte.

---

# 6. Datos exactos para recargar

| Dato | Valor |
|---|---|
| Contrasena de las 6 cuentas | `DemoTFinder123!` |
| `mesa_id` con una sola vacante | `2` |
| `sesion_id` abierta | `1` |
| `usuario_id` del GM | `2` |
| Rol para crear mesas por API | `gm` |
| Rol para las consolas `/admin/*` | `admin` |
| TTL del QR | 600 s |
| TTL de la ventana de llamado | 120 s |
| TTL del cache de mesas | 60 s |
| TTL de la sesion en Redis | 86400 s |
| Puerto de Redis en el host | **6390** |
| Puerto AMQP en el host | **5673** |
| Puerto del panel RabbitMQ | **15673** |
| Puerto de MailHog | **8025** |

---

# Anexo A. Lo que no se muestra, y por que

## A.1 Las dos pantallas rotas: creacion y edicion de mesa

**Sintoma.** En `/mesas/nueva`, al pulsar **Guardar Campana**, la pantalla muestra un error y
la mesa no se crea.

**Causa exacta.** El formulario envia un cuerpo en `camelCase` con campos que el servidor no
acepta. El modelo de validacion del backend declara `extra="forbid"`, es decir, **rechaza
cualquier campo que no conozca**, y ademas espera los enteros `nivel_inicial` y
`jugadores_max` en lugar de las cadenas `nivel` y `plazas`.

**Cuerpo que envia el frontend** (reconstruido a mano):

```json
{"nombre":"Mesa UI","sistema":"PF1e","nivel":"3","plazas":4,
 "rangoNivel":"3-5","frecuencia":"semanal","modalidad":"Online",
 "ubicacion":"Remoto","lore":"x","descripcion":"y","vacante":true,
 "destacada":false,"proximaSesion":"2026-10-03",
 "estadoCategoria":"abierta","estado":"Abierta"}
```

**Respuesta real del servidor (400):**

```json
{"error":{"codigo":400,"mensaje":"body.estado: Input should be 'abierta' or 'cerrada';
 body.nivel: Extra inputs are not permitted;
 body.plazas: Extra inputs are not permitted;
 body.rangoNivel: Extra inputs are not permitted;
 body.frecuencia: Extra inputs are not permitted;
 body.modalidad: Extra inputs are not permitted;
 body.ubicacion: Extra inputs are not permitted;
 body.lore: Extra inputs are not permitted;
 body.vacante: Extra inputs are not permitted;
 body.destacada: Extra inputs are not permitted;
 body.proximaSesion: Extra inputs are not permitted;
 body.estadoCategoria: Extra inputs are not permitted"}}
```

> El codigo real es **400**, no 422. El middleware de sobres de error traduce los errores de
> validacion de FastAPI a 400 para unificar el contrato de los cuatro servicios.

**Como crear una mesa igual (por API):**

```bash
curl -s -X POST http://127.0.0.1:8001/api/v1/mesas \
  -H "Authorization: Bearer $GM" -H 'Content-Type: application/json' \
  -d '{"nombre":"Mesa Probe","sistema":"PF1e","nivel_inicial":3,
       "jugadores_max":5,"tono":"Tactico","horario":"Sabado 18:00"}'
```

Respuesta real: **201** con el objeto completo y `jugadores_actuales: 0`.

## A.2 La pantalla `/mis-mesas` (bloqueada por flag, pero con un problema propio)

Si alguien enciende la flag `misMesas` y entra, las tarjetas aparecen con el identificador
crudo de la mesa y **"0/0 Jugadores"**. La causa: el listado de membresias usa
identificadores de mesa en texto (`la-corona-de-carrona`) mientras que las mesas reales del
backend usan enteros. El emparejamiento nunca coincide y cae en un valor por defecto con
cero jugadores. Como la flag esta apagada en el estado de entrega, no afecta a la defensa.

## A.3 Lo que el frontend no consume

De los **37 endpoints `/api/*`** que exponen los cuatro servicios, el codigo del frontend
referencia **16** de ellos (contado sobre el fuente, no sobre la ejecucion). Dos de esos
16 —`event-log` y `pdf/{id}`— estan definidos en el cliente de API pero **ninguna pantalla
los llama**. Quedan **21 endpoints que el frontend nunca referencia**.

Son los mas interesantes para demostrar por terminal, y todos estan en el documento de
infraestructura: el stream SSE, los tres de la DLQ, los dos de la bandeja de correos, el
estado del PDF, el event-log, y los cuatro de builds y feed.
