---
title: "Guion de presentación — TFinder AE2"
subtitle: "Exposición de 15 minutos, con todas las demos en vivo ejecutadas desde la terminal"
date: "Revisión técnica: 2026-09-29"
lang: es-AR
---

## Adaptado a la presentación "¿Qué son los TTRPG?"

**Duración total: 15 minutos**

| Bloque | Responsable | Minutos | Slides |
|---|---|---|---|
| Introducción TTRPG | Leo | 2:00 | 1–4 |
| Transición y evolución | Lucio | 1:00 | 5–6 |
| Backend | Lucio | 5:15 | 7–12 |
| Frontend | Leo | 5:15 | 13–18 |
| Cierre | Ambos | 1:30 | 19 |
| **Total** | | **15:00** | |

> **Todas las demos se ejecutan desde la terminal.** No hay un solo paso en vivo sobre la
> interfaz ni sobre los paneles web de RabbitMQ o MailHog. El navegador se usa únicamente para
> mostrar las diapositivas.
>
> **Todos los comandos y todas las salidas de consola de este guion fueron ejecutados contra el
> stack en vivo** el 2026-09-29, arrancando de un `docker compose down -v`. No hay valores
> inventados. El
> [Anexo](#anexo--cifras-de-esta-presentación) lista las cifras y la tabla de verificación.

---

# Preparación

**10 minutos, antes de hablar. Esta es la primera sección del documento a propósito:** los demos
son todos de terminal, y el estado de la base tiene que estar limpio **antes** de que empiece la
exposición. Si algo falla, se corrige acá y no en vivo.

## Cómo se ejecuta cada demo

Todo corre con un script. Cada uno imprime lo que está mirando, el resultado esperado, y al
final dice si hubo alguna diferencia con lo verificado:

```text
-- la sección
  esperado: ...        lo que tiene que salir, para comparar mientras se habla
  OK     coincidió con lo verificado
  FALLO  no coincidió
```

**En cada slide hay una línea `Ejecutar:` con el comando exacto.** No hay nada que copiar y
pegar: se tipea el comando y se lee.

## Los tres comandos de la preparación

```bash
bash scripts/demo/00-reset.sh
bash scripts/demo/01-preparacion.sh
bash scripts/demo/02-mesas.sh
```

| Orden | Comando | Qué hace | Tiempo |
|---|---|---|---|
| 1 | `00-reset.sh` | **Borra todo** y levanta el stack con datos limpios | ~3 min |
| 2 | `01-preparacion.sh` | Verifica los 4 servicios, el frontend y saca los 4 tokens | ~5 s |
| 3 | `02-mesas.sh` | Estado de las mesas, topología y checklist previo | ~5 s |

Los tres tienen que terminar con **`sin diferencias con lo verificado`**. Si alguno muestra
`FALLO`, ver la sección [Si algo falla](#si-algo-falla) de más abajo.

### Por qué el reset es imprescindible

El `00-reset.sh` es el único que borra estado, y su `docker compose down -v` **no es
opcional**: sin él se arrastran las notificaciones y los mensajes fallidos de corridas
anteriores —en una corrida sin limpiar se llegaron a contar 47 notificaciones acumuladas— y
quedan mesas con el cupo lleno y usuarios de prueba de la corrida previa. La slide 9 necesita
que la mesa 2 tenga **una sola vacante**, y las slides 15 y 16 necesitan que nadie esté unido
todavía.

**El orden importa:** sacar los tokens antes del reset los deja inservibles, porque el reset
borra las sesiones de Redis y con ellas la revocación de cada token.

### Lo que hay que mirar en la salida

Del `01-preparacion.sh`:

```text
TOKEN=243  TOKEN_ADMIN=251  TOKEN_A=260  TOKEN_B=260
```

Los cuatro números distintos de cero. `TOKEN_A` y `TOKEN_B` son de cuentas **nuevas** que el
script registra si hace falta: los tres jugadores de demostración ya son miembros de la mesa 2,
así que la carrera de la slide 9 necesita identidades aparte.

Del `02-mesas.sh`:

```text
mesa 1: Mesa Demo Abierta  2/4  abierta
mesa 2: Mesa Demo Casi Llena  3/4  abierta
mesa 3: Mesa Demo Cerrada  0/6  cerrada
```

La cola de fallidos tiene que dar `[]`.

---

## Mapa de ejecución

Un comando por slide, en orden. Los scripts son independientes: cada uno pide sus propios
tokens, así que cualquiera se puede repetir solo.

| Momento | Slide | Comando |
|---|---|---|
| Antes de hablar | — | `00-reset.sh` → `01-preparacion.sh` → `02-mesas.sh` |
| 3:10 | 8 · Arquitectura | `03-arquitectura.sh bases` |
| 3:45 | 9 · Concurrencia | `04-concurrencia.sh` |
| 5:00 | 10 · Redis | `05-redis.sh` |
| 5:45 | 11 · Asincronía | `06-asincronia.sh` |
| 7:00 | 12 · Seguridad y observabilidad | `07-seguridad.sh` |
| 8:15 | 13 · Frontend | `03-arquitectura.sh rutas` |
| 8:25 | 14 · Capa HTTP única | `03-arquitectura.sh errores` |
| 9:05 | 15 · Idempotencia | `08-idempotencia.sh` |
| 9:50 | 16 · Contratos visibles | `09-recorrido.sh` |
| 11:40 | 17 · Gating | `10-gating.sh` |
| 12:50 | 18 · Testing | `11-testing.sh` |
| Si sobra tiempo | — | `12-qr.sh` |

> **Por qué el 03 tiene tres partes.** Las slides 8, 13 y 14 sostienen el mismo argumento
> —cuatro servicios independientes con la misma forma de contrato— pero están separadas en el
> tiempo por las slides 9 a la 12. Por eso se corre una parte por vez. Sin argumento corre las
> tres, que es lo cómodo para verificar antes de hablar.

---

## Si algo falla

Primero el diagnóstico. Imprime el token con su vigencia, si su sesión sigue en Redis, si los
cuatro servicios comparten el secreto, el estado de la infraestructura, las cuentas y los
últimos logs:

```bash
bash scripts/demo/99-diagnostico.sh
```

Si el problema es que ya se corrió la demo, la salida más simple es esta:

```bash
bash scripts/demo/00-reset.sh && bash scripts/demo/01-preparacion.sh
```

**Los tres motivos más comunes de un `401`:**

1. El token es viejo, de más de 24 h. Se arregla sacando uno nuevo.
2. Redis quedó pausado por la slide 12. El script lo despausa solo con un `trap` en `EXIT`,
   incluso si se interrumpe con Ctrl-C, pero si se cortó a la fuerza puede quedar pausado:
   `docker compose unpause redis`.
3. Se hizo el reset **después** de sacar los tokens.

**Qué no es re-ejecutable:** la slide 9, porque la carrera deja la mesa 2 en 4/4 y necesita
que esté en 3/4. El `02-mesas.sh` avisa si el estado no es el de demostración y te dice qué
correr. Los demás scripts se pueden repetir las veces que quieras.

---

## Si preferís los comandos a mano

`docs/COMANDOS-PRESENTACION-15MIN.txt` tiene todos los comandos, uno por línea, para pegar
directo en la terminal. Los scripts son lo recomendado: tienen la verificación incorporada.

# Slide 1 — ¿Qué son los TTRPG? · 0:00–0:15 · Leo

**[PRESENTAR]**

Buenos días. Somos Lucio Amarilla y Leonardo Czajkowski. Les presentamos **TFinder**, una
plataforma distribuida para buscar y gestionar mesas de **Pathfinder 1.ª edición**.

Antes de entrar en lo técnico, una breve contextualización sobre qué es un TTRPG.

---

# Slide 2 — ¿Qué son? · 0:15–0:50 · Leo

**[PRESENTAR]**

Un TTRPG o juego de rol de mesa es un juego interpretativo-narrativo que deriva de los juegos
de estrategia. Los jugadores describen mediante el diálogo las acciones de sus personajes, y el
éxito de esas acciones depende de un conjunto formal de reglas llamado sistema.

Como dijo John Wick, se podría convertir el ajedrez en un juego de rol si a las piezas se les
dieran nombres y motivaciones propias que determinen sus acciones.

**Ejemplo real de la plataforma:** una mesa de PF1e se describe con exactamente los campos que
devuelve la API —el sistema de reglas, el tono de la crónica, la frecuencia, el nivel inicial y
el cupo de jugadores. Son los datos que un Director de Juego necesita para decidir si abre su
mesa. Es el mismo `GET /mesas` que se muestra en la slide 16, paso 1.

---

# Slide 3 — ¿Cómo se juega? · 0:50–1:30 · Leo

**[PRESENTAR]**

Un jugador actúa como **Director de Juego**: determina las reglas y la ambientación.

El flujo normal es:

- El Director describe el mundo, sus habitantes y una problemática.
- Los jugadores describen cómo reaccionan sus personajes.
- El Director describe el resultado de esas acciones, en base a las reglas o a su criterio.

La mayoría de los sistemas usan dados para determinar el resultado.

**Ejemplo real de la plataforma:** el Director abre una mesa, la deja **abierta**, y cuando se
completa el cupo el sistema lo refleja automáticamente. Nadie cuenta jugadores a mano: el
contador se mueve solo en el `UPDATE` que se muestra en la slide 9.

---

# Slide 4 — ¿Qué sistemas existen? · 1:30–2:00 · Leo

**[PRESENTAR]**

Algunos de los sistemas más conocidos son **Pathfinder**, **Dungeons & Dragons**,
**Daggerheart** y **Call of Cthulhu**.

TFinder está pensado específicamente para **Pathfinder 1.ª edición**, que es el sistema que
usamos como caso de estudio.

**Transición a Lucio:** "Ahora Lucio les cuenta cómo evolucionó TFinder en la AE2."

---

# Slide 5 — Desarrollo del AE2 TFinder · 2:00–2:30 · Lucio

**[PRESENTAR]**

TFinder pasó de ser un monolito CRUD sobre SQLite a un sistema de **4 servicios FastAPI** con
PostgreSQL, Redis, RabbitMQ y un frontend Vue 3.

En números, todos verificados sobre el repositorio: **107 commits** desde AE1, **21
requerimientos funcionales**, **7 ADR**, **23 especificaciones OpenSpec** que contienen **93
requisitos**, y **152 pruebas automatizadas** —130 de backend y 22 de frontend.

---

# Slide 6 — Evolución · 2:30–3:00 · Lucio

**[PRESENTAR]**

La evolución no fue "dividir carpetas". Cambió la **unidad de despliegue** y con ella
aparecieron contratos entre servicios, asincronía real y propiedad de datos.

| Dimensión | AE1 | AE2 |
|---|---|---|
| Despliegue | 1 app FastAPI | 4 servicios FastAPI |
| Persistencia | SQLite | PostgreSQL 16, una base por servicio |
| Propiedad del dato | un esquema | una base por servicio, cero SQL cruzado |
| Autenticación | Ninguna | JWT + revocación en Redis |
| Mensajería | Inexistente | RabbitMQ con DLQ y reintentos |
| Frontend | No existía en el repo | Vue 3, 45 rutas, 45 vistas |
| Pruebas | Manuales | 130 backend + 22 frontend |

**Transición:** "Veamos el backend en detalle."

---

# Slide 7 — Desarrollo: Backend TFinder · 3:00–3:10 · Lucio

**[PRESENTAR]**

Cuatro servicios, cada uno con su base y su responsabilidad. La regla de oro: ningún servicio
lee tablas de otro.

---

# Slide 8 — Arquitectura · 3:10–3:45 · Lucio

**[PRESENTAR]**

| Servicio | Puerto | Responsabilidad |
|---|---|---|
| `mesas_api` | 8001 | Mesas, auth, solicitudes, QR, matchmaking |
| `builds_api` | 8002 | Builds de personaje |
| `feed_api` | 8003 | Feed social y wiki |
| `notif_api` | 8004 | Notificaciones, PDF, email, DLQ |

Cada servicio expone además **tres sondas de salud** —`/health`, `/live` y `/ready`—, que
son la prueba de que son cuatro procesos independientes y no un monolito partido. Las cuatro
respuestas `200` con `"estado":"listo"` ya se vieron en la preparación.

**Regla de oro:** las referencias cruzadas son por ID, sin clave foránea. La regla se verifica
con un `rg` documentado, no con disciplina.

**[MOSTRAR — 15 s]**

> **Ejecutar:** `bash scripts/demo/03-arquitectura.sh bases`

Salida real:

```text
builds_db
feed_db
mesas_db
notif_db
```

Nótese que **no existe una base "tfinder"**: hay cuatro, y cada servicio abre un pool contra la
suya. (En la base también están las cuatro `_test`, que usan las pruebas automatizadas para no
tocar los datos de la demostración; el filtro las deja afuera a propósito.)

---

# Slide 9 — Concurrencia · 3:45–5:00 · Lucio

**[PRESENTAR]**

Dos hilos leen `jugadores_actuales` antes de que ninguno escriba:

```text
Thread A: SELECT -> ve 0     Thread B: SELECT -> ve 0
Thread A: UPDATE = 1         Thread B: UPDATE = 1
```

Ningún `if` en Python lo arregla: el dato ya fue leído.

La solución es **doble barrera**:

1. **Redis** — `SET reserva:vacante:{mesa_id} 1 NX EX 60` → reduce la competencia.
2. **PostgreSQL** — `UPDATE ... WHERE jugadores_actuales < jugadores_max RETURNING id` →
   garantía real.

**La clave:** el `WHERE` y el `SET` están en una sola sentencia. Si Redis se cae, la consistencia
sigue en pie.

**[MOSTRAR — 45 s] — las dos barreras, una por vez**

> Las identidades `$TOKEN_A` y `$TOKEN_B` las crea y usa el propio script, sin que haya que
> definir nada. Son dos cuentas **nuevas** a propósito: los tres jugadores de demostración ya
> son miembros de esta mesa, así que con una de ellos la unión fallaría por otro motivo.

La mesa 2 está en 3/4: queda **una sola vacante**, y dos identidades distintas compiten por ella.

> **Ejecutar:** `bash scripts/demo/04-concurrencia.sh`

Salida real obtenida:

```text
  antes: Mesa Demo Casi Llena 3/4
  A -> HTTP 201: {"id":7,"mesa_id":2,"usuario_id":7,"estado":"aceptada","idem_key":"keyA","fecha":"2026-09-29T19:01:29.104508+00:00"}
  B -> HTTP 409: {"error":{"codigo":409,"mensaje":"Otra solicitud se está procesando para esta mesa, reintentá"}}
  despues: 4/4
```

> **Cuál de los dos gana es aleatorio.** Es una carrera: la primera que llega al `SET NX` se lleva
> la vacante. Se corrió **6 veces** en la verificación y en una de ellas ganó B. Lo que **no**
> cambia, y es lo que hay que decir, es que hay exactamente un `201`, un `409`, y que la mesa
> termina en **4/4**, no en 5/4.

**El `409` que sale no es el de cupo agotado, y esa es la mitad de la demo.** El perdedor no
llegó a tocar PostgreSQL: perdió el `SET NX` de Redis. Para ver la segunda barrera hay que
repetir la llamada **en serie**, cuando ya no hay competencia:

Salida real:

```text
  {"error":{"codigo":409,"mensaje":"Cupo agotado: no quedan vacantes"}}   [409]
```

Los dos `409` distintos son las dos barreras, vistas una por una:

| Situación | Mensaje | Qué lo rechazó |
|---|---|---|
| Dos peticiones simultáneas | `Otra solicitud se está procesando para esta mesa, reintentá` | `SET NX` de Redis, antes de la base |
| Una petición, mesa ya llena | `Cupo agotado: no quedan vacantes` | `UPDATE ... WHERE jugadores_actuales < jugadores_max` |

Y la reserva se libera sola: se puede comprobar que no queda ninguna clave huérfana.

> **Nota para el expositor:** usar dos tokens distintos es lo que hace creíble la demo. Con el
> mismo token, la segunda llamada falla por idempotencia y no por cupo, y el jurado podría
> suspectar "eso fue el mismo usuario".

---

# Slide 10 — Redis · 5:00–5:45 · Lucio

**[PRESENTAR]**

Redis no es el caché y ya: son **seis usos distintos**, con mecanismos y plazos diferentes.

| Uso | Mecanismo | TTL | Invalidación |
|---|---|---|---|
| Sesión | `SETEX sesion:{jti}` | 24 h | `DEL` en logout |
| Caché de mesas | `SETEX cache:mesas:list` | 60 s | `DEL` en cada escritura |
| Idempotencia | `SETEX idem:solicitud:{k}` | 24 h | `DEL` al consumir |
| Reserva de vacante | `SET NX EX` | 60 s | `DEL` en `finally` |
| Ventana de matchmaking | `SETEX llamado:{id}` | 120 s | expira sola |
| QR asistencia | `GETDEL` | 10 min | se consume al usar |

Tres distinciones que importan:

- **Caché = invalidación + TTL.** La invalidación da corrección; el TTL es red de seguridad.
- **QR = `GETDEL`.** Expirar no es lo mismo que consumir: un QR usado no vuelve a validarse.
  `GETDEL` lee y borra en una sola operación atómica, así que dos validaciones simultáneas del
  mismo código no pueden pasar las dos.
- **Ningún uso guarda el dato.** Redis nunca es la fuente de verdad. Si se apaga, el sistema se
  degrada pero no se corrompe.

**[MOSTRAR — 25 s] — invalidación explícita**

> **Ejecutar:** `bash scripts/demo/05-redis.sh`

Salida real:

```text
cache:mesas:list
60
```

Salida real:

```text
(vacío)
```

**Este es el punto de la slide.** El TTL de 60 segundos es solo la red de seguridad. Lo que
garantiza que quien crea una mesa la vea listada de inmediato es el `DEL` en el camino de
escritura. Si el sistema dependiera únicamente del TTL, el usuario crearía una mesa y no la
vería aparecer hasta un minuto después.

> El `-T` en `docker compose exec` no es opcional: sin él el comando se queda esperando la
> entrada estándar y **se come el resto del bloque**. Pasa en los dos comandos de arriba.

---

# Slide 11 — Asincronía · 5:45–7:00 · Lucio

**[PRESENTAR]**

Exchange `tfinder.events` (topic), tres colas de trabajo, una DLQ. Reintentos con backoff
exponencial: **2 s, luego 4 s**, y al tercer fallo el mensaje va a la cola de fallidos
(`MAX_REINTENTOS = 3`).

**La decisión no obvia:** el contador `_intentos` viaja en el **cuerpo** del mensaje. Con
`nack(requeue=True)`, RabbitMQ reencola la copia original y pierde los headers modificados: el
contador no avanza y el mensaje vuelve para siempre. En el cuerpo sobrevive, y de paso viaja
también el `correlation_id`.

**Consumidor idempotente por `event_id`:** un reintento no duplica notificaciones ni PDFs.

**Regla de diseño:** si el resultado determina la respuesta al usuario, es síncrono. Si es un
efecto posterior, va por la cola. Por eso la solicitud de unión responde `201` en el request, y
la notificación del Director llega después por el bus.

**[MOSTRAR — 20 s] — topología, sin abrir el panel**

El panel web de RabbitMQ muestra lo mismo, pero esto se lee en la terminal y además muestra los
**bindings**, que el panel esconde por defecto:

> **Ejecutar:** `bash scripts/demo/06-asincronia.sh`

Salida real:

```text
name	durable	messages_ready	consumers
notif.mesa	true	0	1
notif.sesion	true	0	1
doc.pdf	true	0	1
dlq.general	true	0	0

tfinder.dlx	dlq.general	#
tfinder.events	doc.pdf	doc.pdf.*
tfinder.events	notif.mesa	mesa.*
tfinder.events	notif.sesion	sesion.*
```

Tres colas con un consumidor cada una —son tres hilos dentro de `notif_api`— y la DLQ con cero,
que es lo correcto: nadie la consume automáticamente, la revisa una persona. El exchange de
fallidos `tfinder.dlx` es un binding distinto al de trabajo, y ese `#` es lo que manda a la DLQ
lo que se muere tres veces.

**[MOSTRAR — 45 s] — PDF asíncrono de punta a punta**

Este es el flujo que mejor muestra el diseño, porque atraviesa **tres servicios** con un solo
identificador. Es la segunda mitad del mismo script:

Salida real:

```text
  documento_id=37736002c9a14e41ad20625efd91570e
```

La respuesta completa del `202` fue:

```json
{"estado":"aceptado","documento_id":"37736002c9a14e41ad20625efd91570e",
 "detalle":"turno_enviado"}
```

> **Lo que hay que decir:** el `documento_id` lo genera **quien pide**, no quien produce, y es un
> identificador nuevo en cada ejecución. Por eso el `202` puede devolverlo al instante: todavía
> no existe ningún archivo, solo el turno en la cola. Si lo generara el worker, el cliente
> tendría que esperar.

Salida real:

```text
  [1] {"documento_id":"37736002c9a14e41ad20625efd91570e","tipo":"build","id_origen":1,"estado":"listo","fecha":"2026-09-29T19:02:05.745373+00:00"}
```

Salida real:

```text
  HTTP=200 type=application/pdf bytes=1257
doc.pdf: PDF document, version 1.3, 1 page(s)
```

**Y si se pide el archivo mientras el estado es `en_proceso`, la respuesta es `404` a
propósito**: el cliente tiene que consultar el estado antes de descargar. No es un error del
sistema, es el contrato.

---

# Slide 12 — Seguridad & Observabilidad · 7:00–8:15 · Lucio

**[PRESENTAR]**

- **JWT + sesión en Redis:** el logout revoca de inmediato, no espera a que expire el token.
  Los cuatro servicios consultan la misma clave, así que un logout en mesas-api invalida el
  token en los cuatro. Un JWT solo no se puede invalidar; la clave en Redis es lo que lo hace
  revocable.
- **`/live` responde 200 siempre; `/ready` responde 503 con detalle si una dependencia cae.**
  La distinción importa: el proceso sigue vivo, pero no debe recibir tráfico.
- **`X-Correlation-Id` viaja del request al log, al evento y al consumidor.**

**[MOSTRAR — 25 s] — modo degradado**

> **Ejecutar:** `bash scripts/demo/07-seguridad.sh`

Salida real:

```text
{"estado":"degradado","dependencias":{"postgres":true,"redis":false,"rabbitmq":true}}   [503]
{"estado":"vivo"}   [200]
```

El servicio **no se cae**: sigue respondiendo y dice exactamente qué dependencia falta. Y en el
mismo instante, la sonda de vida sigue en verde. El `unpause` va en el mismo bloque a propósito:
si se olvida, las slides 14 a 18 devuelven `401` porque no hay sesiones en Redis.

**[MOSTRAR — 30 s] — correlación de punta a punta**

> La consulta al `event-log` requiere el token de **admin**, que el script ya trae. El token de
> `gm@` no alcanza: el endpoint pide rol `admin` explícitamente.

Un solo identificador enviado a mesas-api aparece en sus logs **y** en la base de datos del otro
servicio, después de pasar por el bus de mensajes:

> Se usa la **mesa 3**, que está vacía, y no la mesa 1. Es a propósito: cada demo de este guion
> toca una mesa distinta, así ninguna le roba el cupo a la siguiente. Si la correlación usara la
> mesa 1, la slide 16 se encontraría con el cupo lleno y su paso 3 fallaría.

Salida real — los logs del servicio que recibió la petición:

```json
{"ts": 1790708544348, "nivel": "INFO", "servicio": "mesas-api", "mensaje": "request iniciado", "correlation_id": "demo-corr-160224"}
{"ts": 1790708544359, "nivel": "INFO", "servicio": "mesas-api", "mensaje": "request finalizado", "correlation_id": "demo-corr-160224"}
```

Y ahora, en **notif_api**, otro proceso y otra base de datos:

```json
[{"id":11,"entidadTipo":"mesa.aceptada","entidadId":null,"accion":"consumido","usuarioId":null,"metadata":{"mesa_id":1},"ocurridoEn":"2026-09-29T19:02:24.359824+00:00","correlationId":"demo-corr-160224"}]
```

Eso es trazabilidad distribuida, sin instrumentar nada: el identificador viaja en la cabecera
del request y **dentro del cuerpo del mensaje**, porque las cabeceras AMQP no sobreviven al
reintento.

> La consulta usa `$CID` y no el identificador escrito a mano. En versiones anteriores de este
> guion el comando traía el ID literal de la corrida de verificación, y en vivo no encontraba
> nada: el identificador cambia cada vez que se manda `date`.

**Transición a Leo:** "Hasta acá el backend. Leo les muestra cómo el frontend hace visibles
estos contratos."

---

# Slide 13 — Desarrollo: Frontend TFinder · 8:15–8:25 · Leo

**[PRESENTAR]**

El frontend es una aplicación Vue 3 con **45 rutas y 45 vistas**. Todo pasa por una sola capa
HTTP. Las tres cifras se comprueban desde la terminal:

> **Ejecutar:** `bash scripts/demo/03-arquitectura.sh rutas`

Salida real:

```text
  rutas:  45
  vistas: 45
```

---

# Slide 14 — Capa HTTP única · 8:25–9:05 · Leo

**[PRESENTAR]**

Todo el frontend pasa por una sola función: `api(servicio, ruta, opciones)`.

Eso permite cambiar en un archivo, no en quince:

- Timeout de 8 s con `AbortController`.
- `Authorization` condicional (nunca `Bearer null`).
- `Idempotency-Key` **solo cuando hay body**.
- `X-Correlation-Id` en cada request — el mismo identificador del backend, enviado desde el
  navegador.
- Manejo central del `401` con redirección y `redirect` preservado.
- `ApiError` con `codigo`, `mensaje` y `detalles`, que mapea el sobre de error común de los
  cuatro servicios.

**[MOSTRAR — 30 s] — el sobre de error, en los cuatro servicios**

Ese `ApiError` no es una invención del frontend: los cuatro servicios devuelven **exactamente la
misma forma**. Un `404` a una ruta inexistente da el mismo cuerpo en los cuatro:

> **Ejecutar:** `bash scripts/demo/03-arquitectura.sh errores`

Salida real:

```text
  8001 -> {"error": {"codigo": 404, "mensaje": "Recurso no encontrado"}} [404]
  8002 -> {"error": {"codigo": 404, "mensaje": "Recurso no encontrado"}} [404]
  8003 -> {"error": {"codigo": 404, "mensaje": "Recurso no encontrado"}} [404]
  8004 -> {"error": {"codigo": 404, "mensaje": "Recurso no encontrado"}} [404]
```

Y cuando el error es de dominio, el mensaje es el que el usuario puede entender, no un genérico:

```text
{"error":{"codigo":404,"mensaje":"Mesa 99999 no encontrada"}}   [404]
```

**Por qué importa:** el frontend tiene un solo traductor de errores porque el servidor tiene una
s sola forma de errores. `codigo` es el que decide el comportamiento —el `401` borra la sesión y
redirige, el `409` muestra "sin vacantes"— y `mensaje` es el que se muestra tal cual, sin
traducir nada en el cliente.

---

# Slide 15 — Idempotencia · 9:05–9:50 · Leo

**[PRESENTAR]**

El backend garantiza que la misma clave devuelve el mismo resultado. Pero eso solo sirve si el
cliente **reutiliza la clave**.

En la interfaz la clave se indexa por par `(mesa, usuario)` en `localStorage`, así que un doble
clic o una recarga reenvían el mismo valor. La clave se arma como `{usuario}-{mesa}-{timestamp}`
y viaja en la cabecera `Idempotency-Key`.

**[MOSTRAR — 35 s] — el replay, en la terminal**

La versión en terminal es la misma prueba, y más fuerte: muestra que el servidor no creó una
fila nueva ni consumió otra vacante.

> Las tres llamadas van contra la **mesa 3**, la que está vacía, por la misma razón que la slide
> 12: para que las demos no se pisen el cupo entre sí.

> **Ejecutar:** `bash scripts/demo/08-idempotencia.sh`

Salida real:

```text
  Idempotency-Key=idem-demo-1790709018
  {"id":9,"mesa_id":3,"usuario_id":2,"estado":"aceptada","idem_key":"idem-demo-1790709018","fecha":"2026-09-29T19:10:18.049424+00:00"}  [201]
  {"id":9,"mesa_id":3,"usuario_id":2,"estado":"aceptada","idem_key":"idem-demo-1790709018","fecha":"2026-09-29T19:10:18.049424+00:00"}  [201]
  {"id":10,"mesa_id":3,"usuario_id":2,"estado":"aceptada","idem_key":"idem-demo-1790709018-bis","fecha":"2026-09-29T19:10:18.072857+00:00"}  [201]
```

**Las dos primeras respuestas son idénticas byte a byte: mismo `id`, misma `fecha`.** El replay
no es un error, es un `201` con el resultado guardado. La tercera, con otra clave, sí crea la fila
16. Por eso la clave tiene que ser estable en el cliente: si fuera aleatoria por llamada, un
doble clic crearía dos solicitudes distintas y ambas podrían ocupar vacantes.

La clave vive en **dos lugares**, y se puede ver en los dos:

Salida real:

```text
 id | mesa_id | usuario_id |  estado  |         idem_key
----+---------+------------+----------+--------------------------
 12 |       3 |          5 | aceptada | sse-1790709028
 11 |       1 |          5 | aceptada | guia-1790709027
 10 |       3 |          2 | aceptada | idem-demo-1790709018-bis
(3 rows)

idem:solicitud:idem-demo-1790709018
idem:solicitud:idem-demo-1790709018-bis
idem:solicitud:keyB
idem:solicitud:k-demo-corr-161016
  TTL de la clave = 86373
```

Una sola fila en Postgres para la clave repetida —el `id` 9 aparece una vez—, y la misma clave
en Redis con 24 h de plazo. Si Redis se apaga, el backend cae a la consulta por
`(mesa, usuario, idem_key)` en la base y sigue devolviendo el mismo `id`: la idempotencia no
depende del caché.

---

# Slide 16 — Contratos visibles · 9:50–11:40 · Leo

**[PRESENTAR]**

Un backend asíncrono con un cliente que muestra un spinner infinito no se percibe como asíncrono:
se percibe como roto. El frontend traduce cada contrato a un estado visible:

| Contrato backend | Estado visible en pantalla |
|---|---|
| `201` / `409` de la carrera | "Solicitud enviada" / "Sin vacantes" |
| `GETDEL` del QR | "QR ya utilizado" — no un error de red |
| Notificaciones por evento | Badge que se actualiza en vivo por SSE |
| TTL de Redis en matchmaking | Contador que baja cada 2 s |
| Errores con sobre común | Toast con el mensaje real del servidor |

**[MOSTRAR — 1:50] — el mismo recorrido de la aplicación, en la terminal**

Ocho pasos sobre datos reales del backend. Los pasos 1 a 6 son la aplicación funcionando; los
pasos 7 y 8 son dos pantallas que **no tocan el backend**, y el script lo demuestra.

> **Ejecutar:** `bash scripts/demo/09-recorrido.sh`
>
> Los ocho pasos salen en orden, uno debajo del otro. Tarda unos 15 segundos.

**1 — El listado, con el filtro "con vacantes"**

```text
  1  Mesa Demo Abierta  2/4  PF1e
  4  Mesa Demo Para Invalidar  0/4  PF1e
```

> **Aparecen dos, y es lo correcto.** La mesa 4 es la que creó la slide 10 al demostrar la
> invalidación de caché: acaba de insertarse en la base y por eso tiene lugar. La mesa 2 no
> aparece porque la slide 9 ya la llenó. Es el mejor recordatorio de que el listado es un dato
> vivo de la base, no un JSON de demostración.

**Lo que hay que decir:** el filtro es del cliente, no del backend —`GET /mesas` no acepta
parámetros de consulta y devuelve las cuatro mesas. Lo que viene de la API son los números, y
esos son los que hacen el filtro posible.

**2 — El detalle de una mesa**

```text
{"id":1,"nombre":"Mesa Demo Abierta","jugadores_actuales":2,"jugadores_max":4,"estado":"abierta"}
```

**3 — Unirse: `jugador3@` sobre la mesa 1, que tiene lugar**

```text
{"id":17,"mesa_id":1,"usuario_id":5,"estado":"aceptada","idem_key":"guia-1790708580","fecha":"2026-09-29T19:03:00.613344+00:00"}  [201]
```

> **Crítico para que no falle.** Los tres jugadores de demostración ya son miembros de la Mesa
> Demo Casi Llena. Si se intenta unirse a esa mesa con cualquiera de ellos, no hay vacante libre.
> Por eso el paso 3 usa la **Mesa Demo Abierta** con `jugador3@`.

**4 — El contador se movió en la base**

Este paso usa el endpoint de **detalle** y no el listado, y no es casualidad: el listado se
sirve de `cache:mesas:list` y hay un límite declarado de esta demo (ver la nota al pie).

```text
  Mesa Demo Abierta: 3/4
```

> **Límite declarado, verificado:** el listado cacheado `GET /api/v1/mesas` se invalida al crear,
> editar y borrar una mesa, pero **no** cuando una unión incrementa `jugadores_actuales`. Después
> de unirse, el listado puede mostrar el contador viejo hasta que expire el TTL de 60 s, mientras
> el detalle y la base ya muestran el nuevo. Por eso el paso 4 consulta el detalle. No rompe la
> consistencia —la fuente de verdad es PostgreSQL— pero es el punto débil conocido de la capa de
> caché, y conviene tenerlo a mano si el jurado pregunta por él.

**5 — La notificación, y la prueba de que no es un `setTimeout`**

El aviso no se generó en el navegador: la unión del paso 3 produjo un evento, `notif_api` lo
consumió de una cola distinta y lo insertó. Con el stream abierto antes de la unión, se ve
literalmente el mensaje entrando por SSE:

Salida real:

```text
== lo que llego por SSE ==
data: {"id": 9, "titulo": "Solicitud aceptada", "detalle": "Tu solicitud para la mesa 3 fue aceptada", "entidad": "mesa", "enlace": {"label": "ver mesa", "to": "/mesas/3"}}

== lo que quedo guardado ==
[{"id":9,"grupo":"mesas","icono":"solicitud","leida":false,"autor":null,"mensaje":"Solicitud aceptada","entidad":"mesa","detalle":"Tu solicitud para la mesa 3 fue aceptada","enlace":{"to":"/mesas/3","label":"ver mesa"},"fecha":null,"creado_en":"2026-09-29T19:10:28.451070+00:00"}]
```

**6 — Matchmaking: el TTL de Redis contándose en vivo**

Salida real:

```text
  {"id":2,"mesa_id":1,"estado":"abierto","llamada_abierta_at":"2026-09-29T19:02:41.970098+00:00","fecha_creacion":"2026-09-29T19:02:41.970098+00:00","matchmaking_id":2,"expira_en":120}
  t+2s {"estado":"abierto","ttl_restante":120}
  t+4s {"estado":"abierto","ttl_restante":118}
  t+6s {"estado":"abierto","ttl_restante":116}
```

**7 — `/encuentros`: una pantalla que no toca el backend**

No hay endpoint, y eso es lo que hay que demostrar. El cálculo es del cliente: la vista no
importa la capa de API y tira los dados con un `Math.random()`:

Salida real:

```text
== imports de la API en la vista ==
0
== la vista de encuentros en el cliente de la API ==
0
== de donde sale el resultado ==
16:const BESTIARIO = {
57:  const d20 = 1 + Math.floor(Math.random() * 20)
58:  const criaturas = BESTIARIO[entorno.value] || BESTIARIO['Ruinas subterráneas']
```

**0 imports y 0 endpoints.** La función está detrás de un feature flag activo, y aun así no
necesita backend. Es el caso honesto: no todo lo que parece una pantalla es una consulta.

**8 — `/admin/estadisticas`: diez pantallas que son datos de demostración**

Tampoco hay endpoint, y también a propósito: las diez vistas de administración importan **JSON
estático** y simulan 350 ms de latencia. No llaman a la API. Se comprueba con dos comandos:

Salida real:

```text
== de donde salen los datos de admin ==
import moderacionData from '@/data/admin/moderacion.json'
import usuariosData from '@/data/admin/usuarios.json'
import estadisticasData from '@/data/admin/estadisticas.json'
import plataformaData from '@/data/admin/plataforma.json'
import trazabilidadData from '@/data/admin/trazabilidad.json'
import observabilidadData from '@/data/admin/observabilidad.json'
import dlqData from '@/data/admin/dlq.json'
import resilienciaData from '@/data/admin/resiliencia.json'
import comparadorData from '@/data/admin/comparador.json'
import prometheusData from '@/data/admin/prometheus.json'

const LATENCIA_SIMULADA_MS = 350
const latencia = (ms = LATENCIA_SIMULADA_MS) => new Promise((resolve) => setTimeout(resolve, ms))
== llamadas a la API en las vistas de admin ==
0
```

**Y lo que hay detrás del flag sí es real.** El mismo rol `admin` sí tiene endpoints de
observabilidad que el backend responde de verdad. La frontera se comprueba con dos llamadas:

Salida real:

```text
  {"ok":true}   [200]
  {"error":{"codigo":403,"mensaje":"Rol insuficiente"}}   [403]
  []   [200]
```

**Lo que hay que decir en el paso 5 y en el 8:** el mismo feature gate cubre las dos
situaciones. En `/encuentros` está **encendido** y aun así la pantalla es de cliente; en
`/admin/estadisticas` está **apagado** y además los datos serían de mentira. El flag no dice
"esto consulta la base": dice "esto está terminado". Por eso el paso 8 termina con los endpoints
de admin reales, que son los que de verdad muestran la DLQ y la trazabilidad.

---

# Slide 17 — Gating y modo degradado · 11:40–12:50 · Leo

**[PRESENTAR]**

**20 features, 7 activas, 13 bajo `ComingSoon`.** El gating está en tres lugares coordinados:
banderas, rutas y navegación.

`resolveGuard()` es una **función pura**: la matriz completa de acceso se testea sin montar un
router ni un componente. El feature gate se evalúa **antes** que la autenticación: un invitado
que navega a una función desactivada ve "Próximamente", no el login.

**[MOSTRAR — 30 s] — los banderas, contadas desde el código**

> **Ejecutar:** `bash scripts/demo/10-gating.sh`

```text
  features: 20 | activas: 7 | comingSoon: 13
```

**[MOSTRAR — 30 s] — la matriz, ejecutada en la terminal**

El test de la matriz de acceso corre entero en el terminal, con los nombres de cada caso:

Salida real:

```text
 ✓ tests/unit/feature-gating.spec.js > funcionalidades próximas > redirige una función deshabilitada 1ms
 ✓ tests/unit/feature-gating.spec.js > funcionalidades próximas > permite una función habilitada 0ms
 ✓ tests/unit/feature-gating.spec.js > funcionalidades próximas > permite encuentros, que no necesita backend 0ms
 ✓ tests/unit/feature-gating.spec.js > funcionalidades próximas > permite una ruta habilitada 0ms
 ✓ tests/unit/feature-gating.spec.js > funcionalidades próximas > mantiene la redirección de acceso protegido 0ms
 ✓ tests/unit/feature-gating.spec.js > funcionalidades próximas > envía al administrador a explorar mesas 0ms

 Test Files  1 passed (1)
      Tests  6 passed (6)
```

**La línea que hay que señalar es la tercera:** "permite encuentros, **que no necesita
backend**". Es el mismo caso de la slide 16, paso 7, sostenido por una prueba y no por una
afirmación.

> **Por qué el orden importa:** si el chequeo de rol corriera primero, un invitado que escribe
> `/admin/estadisticas` en la barra vería la pantalla de login —lo cual sería razonable en un
> sitio protegido. Pero como la feature está apagada, ve "Próximamente", que es la respuesta
> honesta: esa pantalla todavía no existe. El flag se evalúa primero justamente para no prometer
> una función antes de construirla. En el código son dos líneas distintas: el flag en
> `guard.js:5` y el chequeo de rol en `guard.js:9`.

**Modo degradado explícito:** si las notificaciones no llegan, la campana se atenúa en lugar de
mostrar "cero". Decir "cero notificaciones" cuando en realidad falló la consulta sería mentirle
al usuario. La parte del backend de esto ya se mostró en la slide 12: el proceso no se cae,
dice qué dependencia falta.

**Lo que se muestra de las 13 funciones apagadas:** no es una lista de pendientes, es el sistema
de interruptores funcionando. Los nombres están en la salida de arriba.

---

# Slide 18 — Testing · 12:50–13:30 · Leo

**[PRESENTAR]**

**22 pruebas de frontend: 15 unitarias y 7 de integración.**

- `feature-gating.spec.js` — matriz de guard completo (6 casos).
- `components.spec.js` — render y estados (5 casos).
- `inventory.spec.js` — humo: todos los módulos importan (4 casos).
- `http.spec.js` y `services.spec.js` — headers inyectados, `409` → `ApiError`, normalización
  `snake → camel`, login → me → logout (7 casos de integración).

`inventory.spec.js` no prueba comportamiento, pero detecta un archivo roto al importarse. Es la
clase de fallo que ninguna otra prueba cubre.

**[MOSTRAR — 25 s]**

> **Ejecutar:** `bash scripts/demo/11-testing.sh`

Salida real:

```text
 ✓ tests/unit/components.spec.js (5 tests) 33ms
 ✓ tests/unit/inventory.spec.js (4 tests) 3ms

 Test Files  3 passed (3)
      Tests  15 passed (15)
   Duration  1.41s
```

Junto a esto, **130 pruebas de backend**: 50 unitarias y 80 de integración, estas últimas contra
PostgreSQL, Redis y RabbitMQ reales, con bases de datos y un *vhost* propios para no tocar los
datos de la demostración.

Salida real:

```text
50 passed, 50 deselected, 1 warning in 0.44s
80 passed, 50 deselected, 1 warning in 9.62s
```

**Transición al cierre:** "Con esto cerramos la parte de frontend."

---

# Slide 19 — Lo que se logró / Lo que sostiene el resultado · 13:30–15:00 · Ambos

**[LUCIO]**

## Lo que se logró

- **Backend:** 4 servicios, una base por servicio, doble barrera para concurrencia, DLQ con
  reintentos, observabilidad con correlación.
- **Frontend:** 45 rutas, capa HTTP única, 22 pruebas, feature gating y contratos visibles.
- **Juntos:** 152 pruebas automatizadas, 21 requerimientos funcionales, 7 ADR, 23
  especificaciones OpenSpec.

**[LEO]**

## Lo que sostiene el resultado

Tres invariantes que se verifican, no se declaran:

1. La consistencia de datos **no depende de Redis**. La garantía está en el
   `UPDATE ... RETURNING` de PostgreSQL. — *Probado en la slide 9: los dos `409` son de dos capas
   distintas.*
2. El productor **no importa nada del consumidor**. Los efectos posteriores van por eventos. —
   *Probado en la slide 11: el `202` vuelve antes de que exista el archivo.*
3. Cada contrato tiene **una forma única**, con un test o un comando que la comprueba. —
   *Probado en la slide 14: el mismo `{"error":{"codigo","mensaje"}}` en los cuatro servicios.*

**[LUCIO]**

## Límites declarados

Sin outbox transaccional · SSE process-local · sin `UNIQUE` en `idem_key` · PDF sin volumen
Docker · sin refresh de token en el cliente · el QR ata al emisor con su propia asistencia ·
**el listado cacheado de mesas no se invalida cuando una unión incrementa el contador** (el
detalle y la base sí están al día; solo el `GET /mesas` puede ir hasta 60 s atrasado).

Ninguna afecta la consistencia de los datos: la fuente de verdad es PostgreSQL. La del listado
sí afecta lo que ve el usuario, y es la ruta natural de AE4 junto con el outbox y el `UNIQUE`.

**[LEO]**

## Demos ejecutadas

Todas desde la terminal, todas verificadas antes de escribir este guion.

| # | Demo | Resultado verificado |
|--:|---|---|
| 1 | Carrera por la última vacante | un `201` y un `409`; mesa queda en 4/4 |
| 2 | Las dos barreras de concurrencia | `409` por lock de Redis, y `409` por cupo, en la misma mesa |
| 3 | Invalidación de caché | lista vacía después de escribir |
| 4 | PDF asíncrono | `202` → `listo` → PDF de 1257 bytes |
| 5 | `/ready` degradado con Redis pausado | `503` con el mapa de dependencias, `/live` en `200` |
| 6 | Correlación de punta a punta | un ID en los logs y en `event_log` |
| 7 | Sobre de error común | el mismo `404` en los cuatro servicios |
| `03-arquitectura.sh bases` | Replay de idempotencia | dos `201` con el mismo `id`, una sola fila |
| `04-concurrencia.sh` | Notificación por SSE | el mensaje entra por el stream después del evento |
| `05-redis.sh` | QR de un solo uso | `200` y luego `409` con el mismo código |
| `06-asincronia.sh` | Matriz de gating | 6 casos, con el flag cortando antes del rol |
| `07-seguridad.sh` | Pruebas | 130 de backend y 22 de frontend |

**[AMBOS]**

Gracias. ¿Preguntas?

---

# Resumen de tiempos

| Slide | Tema | Responsable | Arranca | Duración |
|---|---|---|---|---|
| 1 | Portada y nombres | Leo | 0:00 | 0:15 |
| 2 | Qué es un TTRPG | Leo | 0:15 | 0:35 |
| 3 | Cómo se juega | Leo | 0:50 | 0:40 |
| 4 | Sistemas existentes | Leo | 1:30 | 0:30 |
| 5 | El AE2 en números | Lucio | 2:00 | 0:30 |
| 6 | Evolución AE1 → AE2 | Lucio | 2:30 | 0:30 |
| 7 | Intro del backend | Lucio | 3:00 | 0:10 |
| `03-arquitectura.sh bases` | Arquitectura | Lucio | 3:10 | 0:35 |
| `04-concurrencia.sh` | Concurrencia | Lucio | 3:45 | 1:15 |
| `05-redis.sh` | Redis | Lucio | 5:00 | 0:45 |
| `06-asincronia.sh` | Asincronía y PDF | Lucio | 5:45 | 1:15 |
| `07-seguridad.sh` | Seguridad y observabilidad | Lucio | 7:00 | 1:15 |
| `03-arquitectura.sh rutas` | Intro del frontend | Leo | 8:15 | 0:10 |
| `03-arquitectura.sh errores` | Capa HTTP única | Leo | 8:25 | 0:40 |
| `08-idempotencia.sh` | Idempotencia | Leo | 9:05 | 0:45 |
| 16 | Contratos visibles + recorrido | Leo | 9:50 | 1:50 |
| `10-gating.sh` | Gating y modo degradado | Leo | 11:40 | 1:10 |
| `11-testing.sh` | Testing | Leo | 12:50 | 0:40 |
| 19 | Cierre | Ambos | 13:30 | 1:30 |
| **Total** | | | | **15:00** |

**Por bloque:**

| Bloque | Responsable | Slides | Tiempo |
|---|---|---|---|
| Introducción TTRPG | Leo | 1–4 | 2:00 |
| Transición y evolución | Lucio | 5–6 | 1:00 |
| Backend | Lucio | 7–12 | 5:15 |
| Frontend | Leo | 13–18 | 5:15 |
| Cierre | Ambos | 19 | 1:30 |
| **Total** | | | **15:00** |

---

# Notas para la exposición

## Lucio — Backend

- **Slide 9 (Concurrencia):** es el momento más fuerte, y ahora tiene **dos** demostraciones en
  vez de una. La carrera da el `409` del lock de Redis; la llamada en serie da el `409` del cupo.
  Decir los dos mensajes en voz alta es lo que prueba la doble barrera, no solo el `201` contra
  `409`.
- **Slide 11 (Asincronía):** la decisión del contador en el cuerpo es la más interesante.
  Explicar por qué `nack(requeue=True)` no funciona. El PDF asíncrono es el remate: tres
  servicios, un solo identificador.
- **Slide 12 (Seguridad):** la pausa de Redis es la demo más rápida y más visual del bloque. El
  `unpause` va en el mismo bloque de código, no en uno aparte: si se olvida, todo lo que sigue
  devuelve `401`.

## Leo — Frontend

- **Slide 16:** es la más larga, 1:50. Con las demos en terminal se puede ir más rápido que antes.
  Los pasos 7 y 8 son los que más conviene no apurar: son los que muestran que el gating y la
  separación cliente-servidor se pueden **demostrar**, no afirmar.
- **Slide 17 (Gating):** mencionar que 13 features están apagadas **por diseño**, y que la
  tercera línea del test —"permite encuentros, que no necesita backend"— es el mismo caso que
  el paso 7 de la slide anterior. Conectar las dos.
- **Slide 18 (Testing):** `inventory.spec.js` es el caso más interesante, y `feature-gating` ya
  se vio correr en la slide anterior.

## Si el tiempo se acorta

- **Recortar:** slide 10 (Redis) a 30 s — mostrar solo la invalidación, sin el TTL. Slide 18
  (Testing) a 30 s — mencionar solo los conteos. Slide 17 a 45 s.
- **Mantener sí o sí:** slide 9 (las dos barreras) y slide 16 (recorrido completo).
- **Cierre:** los tres invariantes son lo más importante. Recortar las demos enumeradas, no los
  invariantes.

## Si el tiempo se alarga

- **Agregar:** el flujo del fan-out de correo —publicar `sesion.confirmada` a mano y ver cómo
  `notif_api` pide por HTTP la lista de miembros a `mesas_api` y les escribe a todos—, que es el
  único cruce entre servicios del proyecto.
- **O bien:** insistir en la demo del QR, que devuelve `200` y luego `409` con el mismo código.
  Sale en cuatro líneas:

> **Ejecutar:** `bash scripts/demo/12-qr.sh`

```text
{"asistencia":"registrada"}  [200]
{"error":{"codigo":409,"mensaje":"QR vencido o ya utilizado"}}  [409]
```

> El `usuario_id` del cuerpo tiene que ser el del **emisor** del QR. Con el token de `gm@` ese
> id es el **2**; por eso el comando usa `2` y no el de otra cuenta.

---

# Anexo — Cifras de esta presentación

Todas verificadas por ejecución sobre el repositorio el 2026-09-29.

| Dato | Valor | Cómo se comprobó |
|---|---|---|
| Commits desde AE1 | 107 | `git rev-list --count HEAD` |
| Especificaciones OpenSpec | 23 | `ls openspec/specs \| wc -l` |
| Requisitos OpenSpec | 93 | suma de `requirementCount` |
| ADR | 7 | `ls docs/ADR` |
| Rutas del router | 45 | `grep -cE "^\s+\{ path: '" tfinder-vue/src/router/index.js` |
| Vistas | 45 | `find tfinder-vue/src/views -name '*.vue' \| wc -l` |
| Feature flags | 20 (7 activas, 13 apagadas) | `tfinder-vue/src/config/features.js`, contado con `node -e` |
| Pruebas backend | 130 (50 unit, 80 integración) | `pytest -m unit` y `pytest -m integration` |
| Pruebas frontend | 22 (15 unit, 7 integración) | `npm run test:unit` y `npm run test:integration` |
| Total de pruebas | 152 | 130 + 22 |
| Endpoints `/api/*` | 37, más 12 de salud | OpenAPI de los 4 servicios |
| TTL sesión Redis | 86400 s | `TTL sesion:{jti}` en vivo |
| TTL caché de mesas | 60 s | `TTL cache:mesas:list` en vivo |
| TTL idempotencia | 86400 s | `TTL idem:solicitud:{key}` en vivo |
| TTL QR | 600 s | `qr_asistencia.py` |
| TTL ventana de llamado | 120 s | decreciendo en vivo, 120 → 118 → 116 |
| Backoff de reintentos | 2 s, luego 4 s | `2 ** intentos`, `MAX_REINTENTOS=3` |
| Tamaño del PDF generado | 1257 bytes | descarga real |
| Latencia simulada de admin | 350 ms | `services/admin.js` |

## Verificación de la presentación

Los **catorce scripts** de `scripts/demo/` se ejecutaron contra el stack **en orden**, arrancando
de un `00-reset.sh` completo. Cada script compara lo que obtiene contra lo verificado y cuenta
las diferencias. Resultado: **los doce de la exposición en verde, sin diferencias**, y en un
segundo ciclo sin reset los únicos que marcan diferencias son `02` y `04`, que avisan que
falta el reset.

Estas son las comprobaciones que hacen:

| Script | Qué mide | Resultado verificado |
|---|---|---|
| `01-preparacion.sh` | Los 4 `/ready` | los cuatro `200` con `"estado":"listo"` |
| `01-preparacion.sh` | Frontend | `:5173` en `200`, y el proxy a las APIs en `200` |
| `01-preparacion.sh` | Los 4 tokens | `243 / 251 / 260 / 260`, los cuatro distintos de cero |
| `01-preparacion.sh` | Un token, 4 servicios | `200` en los cuatro |
| `01-preparacion.sh` | `alta()` repetido | los mismos tokens la segunda vez, sin `400` |
| `02-mesas.sh` | Estado de las mesas | mesa 1 en `2/4`, mesa 2 en `3/4` |
| `02-mesas.sh` | Miembros | mesa 1: dos jugadores; mesa 2: los tres |
| `02-mesas.sh` | Colas | 4 colas, 3 con 1 consumidor, DLQ con 0 |
| `02-mesas.sh` | Bindings | `tfinder.events` a 3 colas + `tfinder.dlx` a la DLQ |
| `02-mesas.sh` | Cola de fallidos | `[]` con el token de admin |
| `03-arquitectura.sh bases` | Las 4 bases | `builds_db`, `feed_db`, `mesas_db`, `notif_db` |
| `04-concurrencia.sh` | Carrera con 2 tokens | un `201` y un `409`; mesa queda en 4/4 |
| `04-concurrencia.sh` | La carrera, 6 veces | siempre 1 `201` + 1 `409`; el ganador cambió una vez |
| `04-concurrencia.sh` | Barrera 2, en serie | `409` "Cupo agotado: no quedan vacantes" |
| `04-concurrencia.sh` | Reserva liberada | ninguna clave `reserva:*` colgada |
| `05-redis.sh` | Caché recién escrita | `cache:mesas:list` con TTL `60` |
| `05-redis.sh` | Caché después de escribir | lista vacía — la invalidación funcionó |
| `06-asincronia.sh` | Colas y bindings | igual que en la preparación, en vivo |
| `06-asincronia.sh` | PDF asíncrono | `202` → `listo` → `HTTP=200`, 1257 bytes, PDF válido |
| `07-seguridad.sh` | `/ready` con Redis pausado | `503` con el mapa de dependencias |
| `07-seguridad.sh` | `/live` con Redis pausado | `200` — sigue vivo |
| `07-seguridad.sh` | Tras el `unpause` | vuelve a `"estado":"listo"` |
| `07-seguridad.sh` | Correlación | el mismo ID en los logs y en `event_log` |
| `03-arquitectura.sh rutas` | Rutas y vistas | 45 y 45 |
| `03-arquitectura.sh errores` | Sobre de error común | el mismo `404` en los cuatro servicios |
| `03-arquitectura.sh errores` | Error de dominio | `"Mesa 99999 no encontrada"` |
| `08-idempotencia.sh` | Replay de idempotencia | dos `201` con el mismo `id` y la misma `fecha` |
| `08-idempotencia.sh` | Clave nueva | `id` 16, fila nueva |
| `08-idempotencia.sh` | Persistencia | una sola fila en Postgres, TTL `86400` en Redis |
| `09-recorrido.sh` | Listado con filtro | mesa 1 en 2/4 y la mesa 4 que creó la slide 10; la 2 ya no aparece porque la slide 9 la llenó |
| `09-recorrido.sh` | Unirse a la mesa 1 | `201`, y el contador pasa a 3/4 |
| `09-recorrido.sh` | Notificación por SSE | el mensaje entra por el stream tras el evento |
| `09-recorrido.sh` | Matchmaking | `expira_en: 120`, y el TTL bajando 120 → 118 → 116 |
| `09-recorrido.sh` | Rol incorrecto | `403` "Rol insuficiente" |
| `09-recorrido.sh` | `/encuentros` | 0 imports de API, 0 endpoints, `Math.random` local |
| `09-recorrido.sh` | `/admin/*` | 10 JSON estáticos, 350 ms simulados, 0 llamadas a la API |
| `09-recorrido.sh` | Frontera de roles | `200` con admin, `403` con gm |
| `10-gating.sh` | Conteo de flags | 20 features, 7 activas, 13 apagadas |
| `10-gating.sh` | Matriz de gating | 6 casos, todos en verde |
| `11-testing.sh` | Pruebas frontend | 15 unit + 7 integración |
| `11-testing.sh` | Pruebas backend | 50 unit + 80 integración |
| `12-qr.sh` | QR de un solo uso | `200` y luego `409` con el mismo código |

### Comandos que hubo que corregir

Estaban rotos o daban un resultado engañoso. Se corrigieron y se volvieron a ejecutar. La
columna dice en qué script quedó cada corrección:

| Slide | Qué pasaba | Corrección |
|--:|---|---|
| `03-arquitectura.sh bases` | `psql -U tfinder -c "\l"` fallaba con `database "tfinder" does not exist` | Agregar `-d postgres`: sin base, psql conecta a una llamada como el usuario |
| `03-arquitectura.sh bases` | El filtro `grep` dejaba pasar también las 4 bases `_test` | Exigir el nombre exacto con `grep -E " (mesas\|builds\|feed\|notif)_db "` |
| `04-concurrencia.sh` | El guion afirmaba que el `409` de la carrera era "cupo agotado" | No lo es: es el lock de Redis. Se agregó la segunda llamada en serie para mostrar la barrera de PostgreSQL |
| `05-redis.sh` | `docker compose exec` sin `-T` se come el resto del bloque | Agregar `-T` a todos los `exec` |
| `05-redis.sh` | El TTL salía en `41` porque la clave ya existía de antes | `DEL` de la clave antes de leer, para que el TTL salga en `60` clavados |
| `06-asincronia.sh` | La topología pedía abrir el panel web de RabbitMQ | `rabbitmqctl list_queues` y `list_bindings`, y `grep -vE 'Timeout\|Listing queues'` para quitar el ruido del CLI |
| `07-seguridad.sh` | El `event-log` se consultaba con un ID literal de la corrida anterior | Usar `$CID` en la URL: el identificador cambia en cada corrida |
| `08-idempotencia.sh` | La demo pedía abrir DevTools y leer `localStorage` | Replay con la misma `Idempotency-Key` desde la terminal, más la fila en Postgres y el TTL en Redis |
| 16 | El paso 7 y el 8 no tienen endpoint | Se reescribieron como la demostración de que **no** tocan el backend, con `grep` sobre la vista y `services/admin.js` |
| 12, 15, 16 | Las demos se pisaban el cupo entre sí al correrlas en orden | Cada demo usa una mesa distinta: la 2 para la carrera, la 3 para correlación, idempotencia y SSE, la 1 para unirse |
| `10-gating.sh` | Correr `resolveGuard` con `node --input-type=module` | No funciona: `guard.js:1` importa `@/config`, que es un alias de Vite y Node no resuelve. Se reemplazó por `npx vitest run tests/unit/feature-gating.spec.js` |
| `11-testing.sh` | El conteo decía 19 pruebas de frontend (12 unit) | Son **22** (15 unit). El conteo estático de `it(` daba 12 porque `inventory.spec.js` genera sus 4 casos con un helper |
| 9, 12, 15, 16 | Los `documento_id`, `jti`, fechas y contadores del texto no coincidían con una corrida en orden | Todos los identificadores variables se transcribieron de la corrida final completa, no de corridas aisladas |

### Errores de contenido corregidos

Además de los comandos, dos cifras del guion estaban mal y se corrigieron en todas las slides
en que aparecen:

| Dato | Antes | Ahora | Cómo se comprobó |
|---|---|---|---|
| Pruebas frontend | 19 (12u + 7i) | **22 (15u + 7i)** | `npm run test:unit` → `15 passed` |
| Total de pruebas | 149 | **152** | 130 + 22 |

Y uno de **comportamiento**, encontrado al correr el guion de corrido:

| Qué pasa | Dónde | Consecuencia |
|---|---|---|
| `GET /api/v1/mesas` se sirve de `cache:mesas:list`, y `invalidar_listado()` se llama al crear, editar y borrar una mesa (`controllers/mesas.py:52,61,70`) pero **no** en `ocupar_vacante()` (`models/mesa.py:63-75`) | `mesas_api` | Después de unirse a una mesa, el listado puede mostrar el contador viejo hasta 60 s. El detalle (`GET /mesas/{id}`) y la base sí están al día |

No se corrigió porque queda fuera del alcance de este documento. La demo de la slide 16 lo
esquiva consultando el detalle en el paso 4, y queda declarado como límite conocido en la
slide 19. **La corrección es una línea**: llamar `invalidar_listado()` en
`solicitudes_controller.py` después de `ocupar_vacante`.

### Dependencia entre demos

Cada demo del guion toca una mesa distinta, para que ninguna le robe el cupo a la siguiente.
Esto se detectó corriendo las slides **en orden**, y no por separado:

| Script | Mesa que usa | Cupo al terminar |
|---|---|---|
| `04-concurrencia.sh` — carrera | mesa 2 del seed (3/4) | 4/4 |
| `07-seguridad.sh` — correlación | mesa 3 del seed (0/6) | 1/6 |
| `08-idempotencia.sh` | **mesa propia** (6 vacantes) | 2/6 |
| `09-recorrido.sh` paso 3 | mesa 1 del seed (2/4) | 3/4 |
| `09-recorrido.sh` paso 5 | **mesa propia** (4 vacantes) | 1/4 |

`08-idempotencia.sh` y el paso 5 de `09-recorrido.sh` crean su propia mesa justamente para que
se puedan repetir: si usaran la mesa 3, al segundo ciclo se quedarían sin vacantes y el script
empezaría a dar `409` donde debía dar `201`.

En la versión anterior, la slide 12 llenaba la mesa 1 y la slide 15 devolvía
`409 Cupo agotado` en su tercera llamada, y la slide 16 fallaba en el paso 3. Corregido moviendo
la correlación y la idempotencia a la mesa 3.

## Correcciones respecto de la versión anterior de este guion

| Slide | Antes | Ahora |
|---|---|---|
| — | Preparación al final del documento | **Preparación como primera sección** |
| todas | Comandos para copiar y pegar a mano | **`bash scripts/demo/NN.sh`**, con verificación incorporada |
| 8, 13, 14 | Tres bloques de comandos separados | **`03-arquitectura.sh`** con selector: `bases`, `rutas`, `errores` |
| — | Cada demo usaba la mesa 1 o la 2 sin pensar en el orden | **Mesas separadas por demo**, ver la tabla de dependencia |
| `06-asincronia.sh` | Topología en el panel web de RabbitMQ | **`rabbitmqctl` en la terminal, con bindings** |
| `03-arquitectura.sh errores` | Sin demostración | **El mismo sobre de error en los cuatro servicios** |
| `08-idempotencia.sh` | DevTools y `localStorage` | **Replay de idempotencia desde la terminal** |
| 16 | Demo guiada de 8 pasos en el navegador | **Los mismos 8 pasos con `curl`**, y los pasos 7 y 8 probando que no tocan el backend |
| 16 y 19 | PDF asíncrono en la interfaz | **no existe esa interfaz**; se demonstra por terminal en la slide 11 |
| `10-gating.sh` | Gating mostrado en pantalla | **`vitest` con los 6 casos de la matriz, en la terminal** |
| 5 | 90 commits | 107 |
| 5 | 25 especificaciones | 23 |
| 6 | 46 rutas, 44 vistas | 45 rutas, 45 vistas |
| `05-redis.sh` | 4 usos de Redis | 6 usos |
| `06-asincronia.sh` | `documento_id` fijo en los comandos | variable `$DOC`, porque cambia cada corrida |
| `06-asincronia.sh` | backoff `1s → 2s → 4s` | `2s → 4s` |
| `07-seguridad.sh` | `{"estado":"degradado","redis":false}` | `{"estado":"degradado","dependencias":{...}}` |
| `07-seguridad.sh` | `event-log` con el ID escrito a mano | variable `$CID` |
| 16 | toast "Te uniste" | "Solicitud enviada a «Mesa…»" |
| `10-gating.sh` | 21 features, 14 apagadas | 20 features, 13 apagadas |
| `11-testing.sh` | 19 pruebas (12u + 7i) | **22 pruebas (15u + 7i)** |
| 19 | 149 pruebas | **152 pruebas** |
