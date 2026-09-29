# Informe técnico individual de AE2 — Amarilla Lucio · Backend B01–B12

**Proyecto:** TFinder — plataforma de búsqueda y gestión de mesas de juego de rol
**Asignatura:** Paradigmas y Lenguajes de Programación III — `ISI17PL324`
**Actividad:** `ISI17PL324V26AE2V26` — Actividad de Evaluación 2
**Estudiante:** Amarilla Lucio
**Alcance individual:** backend B01–B12 (issues #14 a #25)
**Rama:** `AE2-Backend`
**Versión base de AE1:** `1781e4efb516cb8ac7c3965d140ba476c932cad2` (2026-08-28)
**Tags de entrega:** `2.0.0` (alfa) y `2.1.0` (beta)
**AÑO:** 2026

> El informe del sistema completo está en [`INFORME-AE2.md`](./INFORME-AE2.md). Este documento se limita a mi alcance individual y profundiza donde la rúbrica pide fundamentación. Las secciones que repiten lo técnico del conjunto remiten a él en lugar de duplicarlo.

---

## 1. Alcance comprometido

### 1.1 Qué me comprometí a hacer

AE2 es una instancia **individual sobre una base grupal**. Mi alcance es la evolución completa del backend, desde la infraestructura de contenedores hasta el cierre documental. Lo comprometí como doce bloques (B01–B12), cada uno con un issue asociado, un commit identificable y una especificación en OpenSpec.

| RF | Título | Issue | Commit | Entregado |
|---|---|---|---|---|
| B01 | Infraestructura y contenedores (Compose: PostgreSQL, Redis, RabbitMQ, MailHog) | #14 | `f892f7d` | Sí |
| B02 | Separación en 4 servicios + PostgreSQL + propiedad de datos | #15 | `8dae133` | Sí |
| B03 | Autenticación JWT, sesiones en Redis, roles y revocación | #16 | `3dd0272` | Sí |
| B04 | Redis: caché con invalidación, TTL de llamado, reserva de vacante | #17 | `6395191` | Sí |
| B05 | Eventos RabbitMQ: topología, ACK, reintentos, DLQ, idempotencia | #18 | `6a70869` | Sí |
| B06 | Concurrencia: doble barrera e `Idempotency-Key` | #19 | `6610e3d` | Sí |
| B07 | QR de asistencia de un solo uso | #20 | `29058f6` | Sí |
| B08 | PDF asíncrono (`202` + worker) | #21 | `20b6849` | Sí |
| B09 | Proveedor de email con outbox | #22 | `756b3f9` | Sí |
| B10 | Observabilidad: logs JSON, correlación, `/live`, `/ready` | #23 | `9f10f66` | Sí |
| B11 | Testing automatizado | #24 | `47008b6` | Sí |
| B12 | Cierre documental: ADRs, OpenAPI, evidencias, tags | #25 | `834af06` | Sí |

```bash
# Verificación de la trazabilidad
git log --oneline 1781e4e..AE2-Backend | wc -l        # 79
git log --format='%h %s' 1781e4e..AE2-Backend | grep -c '#[0-9]'
git tag -l '2.*'                                        # 2.0.0  2.1.0
```

### 1.2 Qué queda explícitamente fuera de alcance

Declarar lo que no hice es parte de la definición del alcance, y evita que la evaluación suponga un alcance que no estaba comprometido.

| Fuera de alcance | Motivo |
|---|---|
| Alta disponibilidad y réplicas | RNF-15 está asignado a AE4. Con 1 réplica por servicio, el `liveness` no puede demonestrar continuidad ante caída |
| CI/CD con publicación de imágenes | RNF-20 es de AE4. Lo entregado es el pipeline de **verificación** (6 jobs), no de despliegue |
| `Prometheus` / `Grafana` / métricas | RNF-19 es de AE4. Hay logs y health checks, no métricas |
| Circuit Breaker | RNF-14 es de AE4. Hay timeouts (8 s en cliente, 3 s en SMTP) y reintentos en el consumidor |
| Pasarela de pagos real | El escenario no la exige para TFinder. El equivalente es el email con sandbox MailHog |
| `database-per-service` físico | Justificado en §4 del informe conjunto: con despliegue conjunto, la separación física agrega fallos sin agregar capacidad |
| E2E en navegador | Verificado por HTTP (99 casos). El gap está declarado en el inventario de testing |
| Endpoints de confirmación de sesión | Necesarios para que el consumidor `notif.sesion` sea alcanzable. Declarado como brecha L8 |

### 1.3 Estado heredado de AE1 y qué cambié

La base AE1 (`1781e4e`) era una aplicación FastAPI única con SQLite. Lo que hice no fue conservarla sino **extraer de ella el dominio y reconstruir la arquitectura**. Concretamente:

| Se conservó | Se reconstruyó |
|---|---|
| El modelo de datos de `Mesa` y sus cinco endpoints públicos | La unidad de despliegue: de 1 aplicación a 4 servicios |
| La semántica del CRUD (`GET`/`POST`/`PUT`/`DELETE`) | La persistencia: de SQLite a PostgreSQL 16 con una base por servicio |
| La convención de capas `routes`/`controllers`/`models` | El sistema de errores: de un manejador local a un envelope único en 4 servicios |
| La estructura de carpetas por capa, replicada por servicio | La configuración: de dos variables a un `.env` con toda la infraestructura |

No hay código de AE1 en el árbol actual. Eso es una decisión, no un descuido: el monolito no tenía una parte reutilizable que no fuera el dominio, y mantener un capa de compatibilidad habría dejado en pie el acoplamiento que AE2 tenía que eliminar.

---

## 2. Evolución arquitectónica

### 2.1 Por qué cuatro servicios y no uno ni ocho

El criterio que usé fue: **un servicio por frontera de negocio, ni más ni menos.**

El argumento para no más de cuatro: la consigna propone servicios por módulo de negocio, y TFinder tiene cuatro contextos acotados reales —mesas e identidad, builds, feed, notificaciones. Partir más habría creado servicios sin frontera propia, que es un monolito distribuido con el costo de operación de un sistema distribuido.

El argumento para no menos de cuatro —es decir, seguir con el monolito— es el que la consigna descarta explícitamente, pero merece una respuesta: el problema no es el tamaño del código, es que **una aplicación monolítica no puede tener contratos entre servicios**. Si las notificaciones se generan en el mismo proceso que las mesas, no hay contrato que definir, no hay frontera que cruzar, y no hay forma de que "se desacoplen" porque nunca estuvieron juntas. La asincronía y la propiedad de datos son propiedades de la **distribución**, y no se pueden simular dentro de un proceso.

La decisión está registrada en [ADR-006](../docs/ADR/ADR-006-servicios.md).

### 2.2 La biblioteca compartida y su frontera

El riesgo real de extraer una biblioteca compartida es convertirla en el nuevo monolito. La regla que sostuve es que **`app/` contiene infraestructura genérica y jamás lógica de dominio**:

```text
app/infra/redis.py       -> get_redis()        sabe cómo conectarse; no sabe qué es una vacante
app/infra/rabbitmq.py    -> publicar()         sabe cómo publicar; no sabe qué es una mesa
app/infra/ready.py       -> evaluar_ready()    sabe consultar dependencias; no sabe qué requiere mesas-api
```

El test que apliqué para decidir si algo entraba en `app/` fue: *¿esta función seguiría siendo correcta si el dominio fuera de otra aplicación?* `get_redis()` sí. `obtener_mesa_por_id()` no, y por eso vive en `mesas_api/app/models/`.

El resultado es que los cuatro servicios comparten ~8 módulos de infraestructura y cero lógica de negocio, y `tests/test_public_surface.py` verifica que todo el paquete `app.*` sea importable y exponga su superficie pública.

### 2.3 La separación de bases y cómo se verifica

Cada servicio tiene su base, su pool y su `schema.sql`. La regla de no leer datos ajenos tiene tres niveles de fuerza, y el tercero es el que la hace real:

1. Cada servicio importa **su** pool. No existe un `get_pool()` global.
2. Las referencias entre dominios son **por id, sin clave foránea**. `builds.mesa_id` es un entero sin FK a `mesas_db.mesas`. Un FK entre bases distintas es imposible en PostgreSQL, y omitirlo documenta que la integridad de esa referencia es responsabilidad de quien la escribe.
3. La regla es **comprobable con un comando**, dado en [`PROPIEDAD_DE_DATOS.md`](./PROPIEDAD_DE_DATOS.md): un `rg` que lista los accesos a la base debe mostrar únicamente el `db.py` del servicio dueño de cada una.

Un principio de arquitectura que no se puede verificar por comando es una declaración de intenciones. El paso 3 es lo que convierte la regla en una invariante del proyecto.

### 2.4 Lo que AE1 no tenía y hubo que decidir desde cero

| Necesidad | Decisión | Dónde |
|---|---|---|
| Cómo se comunica un servicio con otro | REST síncrono para consultas, eventos para efectos | §3 y §5 |
| Dónde vive la fuente de verdad | PostgreSQL; Redis nunca es la única copia | §5 |
| Cómo se manejan los errores entre servicios | Un envelope, dos capas (excepciones + middleware ASGI) | §2.5 |
| Qué pasa si una dependencia no responde | Timeouts explícitos, `/ready` degradado, outbox para el email | §6, §7 |
| Cómo se reconstruye un flujo distribuido | `correlation_id` en logs, request → evento → consumidor | §8 |

### 2.5 El envelope de error: el defecto más instructivo del proyecto

AE2 heredó un problema que no era visible mirando un solo archivo. FastAPI serializa `HTTPException` como `{"detail": "..."}`, y las dependencias de autenticación de cada servicio añadían su propia variante. El sistema tenía **dos convenciones de error simultáneas**, y lo grave no era la inconsistencia en sí sino que un cliente no podía distinguirlas sin conocer cada servicio: un `{"detail": ...}` en la respuesta no indicaba qué código usar ni de qué servicio venía.

La corrección tiene dos capas porque una sola no alcanza. Los manejadores de excepciones (`app/infra/errors.py:73-83`) cubren lo que la aplicación lanza, pero hay errores que Starlette emite **antes** de esa capa: el 404 y el 405 del router. Sin un middleware ASGI, esos dos seguían saliendo en el formato de Starlette, y con un middleware ingenuo el streaming en vivo se rompía.

Por eso el buffering del middleware se condiciona a `status >= 400` **y** content-type JSON **y** ausencia del marcador `x-tfinder-envelope: 1` (`app/middleware/error_envelope.py:106`). Un `200` con `text/event-stream` pasa intacto. Hay un test dedicado a esto —`tests/test_envelope_error.py:102-129`— porque es exactamente el tipo de regresión que un middleware de normalización introduce sin darse cuenta.

Además se unificó `RequestValidationError` a **400** en lugar del 422 por defecto de FastAPI, para que un error de validación se procesara con el mismo camino que cualquier otro.

Este defecto fue encontrado por integración (D-04), no por diseño, y esa es la lección: **el contrato entre servicios solo se verifica cuando hay dos servicios hablando.**

---

## 3. Comunicación síncrona

### 3.1 Superficie pública y su piso contractual

| Servicio | Rutas | Piso en `test_api_contracts.py` |
|---|---|---|
| `mesas_api` | 18 | 18 |
| `builds_api` | 7 | 7 |
| `feed_api` | 6 | 5 |
| `notif_api` | 15 | 9 |

La diferencia entre el conteo real y el piso es deliberada, y es una decisión de diseño del test: un piso que coincidiera exactamente con el presente convertiría **cualquier adición** en un fallo de test, que es la forma más rápida deJX¢emptsar a que se agregan endpoints. El piso protege contra lo que duele —un endpoint borrado sin querer— y deja respirar lo que es legítimo agregar. Por eso `notif_api` tiene 15 rutas y un piso de 9: el piso se fijó cuando había 9, y las 6 restantes son de requisitos posteriores.

### 3.2 El contrato de errores como documentación ejecutable

`tests/test_envelope_error.py` tiene 7 casos parametrizados sobre los cuatro servicios, y uno de ellos (`:46-55`) verifica que los manejadores compartidos sean **el mismo objeto**:

```python
assert mesas_api.app.errors.manejar_http is app.infra.errors.manejar_http
```

Es un test poco habitual y deliberadamente tal: si un servicio alguna vez redefinió su propio manejador, la aserción fallaría. Un test que solo verifica la forma de la respuesta passing detectaría que la forma cambió; este detecta que la forma cambió **en un solo servicio**, que es el caso difícil de ver.

### 3.3 El cliente entre servicios

`notif_api` es el único servicio que consume a otro, y lo hace una vez: para obtener los destinatarios de un email. Lo resuelve por REST (`GET /api/v1/mesas/{id}/miembros`) con una cuenta de servicio, no leyendo `mesas_db.usuarios`.

Es un solo consumidor, y por eso no construí un cliente HTTP compartido sofisticado. Cuando aparezca el segundo consumidor con necesidades distintas, ese es el momento de abstraerlo; antes, la abstracción sería especulativa.

---

## 4. Comunicación asíncrona

### 4.1 Topología y el defecto del DLX

La topología está en §5 del informe conjunto. Lo que es de mi autoría conceptual y merece justificación es el binding de la DLQ, porque **costó encontrarlo y es la clase de defecto que un mock nunca detectaría**:

```text
las 3 colas de trabajo declaran  x-dead-letter-exchange: tfinder.dlx
tfinder.dlx se declara  ✔
dlq.general  se declara       ✔
dlq.general  bound a tfinder.dlx   <-- este paso es OBLIGATORIO
```

Sin ese último paso, cuando un mensaje se rechaza sin requeue, RabbitMQ lo enruta al exchange de errores, descubre que no tiene ninguna cola bound, y **lo descarta sin avisar**. El sistema parecía funcionar: el mensaje desaparecía, nadie lo consumía, y no había error en ninguna parte. El único síntoma era una DLQ siempre vacía.

Apareció como el defecto **D-05** en la verificación E2E. El comentario en `notif_api/app/infra/amqp.py:34-38` documenta la trampa para que nadie la repita, y `tests/test_amqp_topologia.py` la verifica por la **management API**, que es la única forma de inspeccionar bindings (pika no los expone). Ese test podría no existir y el defecto volvería sin que nada lo detectara.

### 4.2 Por qué ACK + republicar y no `nack(requeue=True)`

El diseño de reintentos usa un contador `_intentos` **en el cuerpo del mensaje**, y republica una copia nueva. La alternativa obvia —`nack(requeue=True)`— no funciona, y la razón es precisa: `requeue` reencola **la copia original** del mensaje, con sus headers originales. Cualquier header que el consumidor hubiera modificado se pierde, y el contador no avanza. El resultado es un mensaje que vuelve para siempre, sin que ningún reintento se registre en ningún lado.

Con ACK + republicar, el contador viaja en el body, sobrevive al viaje, y cuando supera `MAX_REINTENTOS = 3` el mensaje aterriza en `dlq.general` con `ultimo_error` y `cola_origen`, y se persiste en la tabla `mensaje_dlq` para que un administrador pueda verlo, reintentarlo o descartarlo.

El backoff es `2 ** intentos` segundos (1 s, 2 s, 4 s) y se aplica con `time.sleep` antes de republicar, que es aceptable en un consumidor síncrono de un solo mensaje (`prefetch_count=1`).

### 4.3 Idempotencia del consumidor

Como el reintento **republica el mismo mensaje**, el mismo `event_id` puede llegar más de una vez al consumidor. Sin una guarda, un reintento generaría una notificación duplicada o un segundo PDF. La guarda es consultar `event_log` por `event_id` antes de aplicar el efecto, y es lo que hace que el reintento sea seguro en lugar de destructivo.

### 4.4 Qué se desacopló y por qué

| Proceso | Mecanismo | Ganancia concreta |
|---|---|---|
| Notificar una unión | Evento `mesa.aceptada` | `mesas_api` no sabe que existe un email. Un SMTP caído no puede impedir una unión |
| Generar un PDF | `202` + `doc.pdf` | El cliente no espera; tiene un `documento_id` para consultar |
| Enviar el email de confirmación | Consumidor + outbox | El fallo de email es recuperable sin repetir la operación de negocio |

La prueba de que el desacoplamiento es real y no declarativo: **ningún productor importa nada de `notif_api`**, y `notif_api` no puede ser invocado por el productor. Si mañana se agrega un segundo consumidor de `mesa.aceptada` —un webhook, un push a la app móvil— no se toca una línea del productor. Ese es el criterio con el que evalué cada decisión de este apartado: si agregar un consumidor obligaba a modificar al productor, la decisión estaba mal.

### 4.5 El punto donde la asincronía NO correspondía

Unirse a una mesa se resolvió **síncronamente**, y esa es la decisión conceptual más importante del proyecto.

El usuario que se une necesita saber si entró o si el cupo se agotó. Esa respuesta **es** el resultado de la operación, no un efecto posterior. Si se hiciera asíncrono, el usuario tendría que esperar un evento para enterarse de algo que ya se sabe, y el problema de la concurrencia no desaparecería: se trasladado al consumidor, que seguiría necesitando exclusión mutua.

La regla que apliqué: **si el resultado determina la respuesta al usuario, es síncrono y la concurrencia se resuelve con exclusión mutua; si el resultado es un efecto posterior, va por la cola.** Todo lo demás se desacopló.

---

## 5. Concurrencia, consistencia e idempotencia

Este es el núcleo del requisito, y es donde más profundicé. El detalle técnico está en §7 del informe conjunto; aquí está el razonamiento.

### 5.1 El problema, demostrado antes de resolverlo

Escribí `tests/repro_carrera.py` **antes** de la corrección, y esa es la decisión de proceso de la que más me Thyroid Sirve. Un test de reproducción que se escribe después de arreglar, valida la solución; escrito antes, prueba que el problema existía.

```text
10 hilos invocan "unirse" sobre una mesa con 1 vacante
sin barreras -> N inserciones, sobreventa
```

La causa no es la escritura duplicada sino la separación entre lectura y escritura:

```text
Thread A: SELECT jugadores_actuales -> ve 0     Thread B: SELECT jugadores_actuales -> ve 0
Thread A: UPDATE jugadores_actuales = 1         Thread B: UPDATE jugadores_actuales = 1
```

Ambos leen antes de que ninguno escriba. Cualquier validación posterior es inútil: el dato ya fue leído. Un `if` en Python no lo arregla, porque el problema no es la condición sino la falta de atomicidad entre las dos operaciones.

### 5.2 Las alternativas que descarté, y por qué

**`SELECT ... FOR UPDATE`.** PostgreSQL bloquea la fila y la segunda conexión espera. Funciona, con dos costos: ocupa un slot del pool bloqueada durante toda la espera, y el lock dura toda la transacción, que es más larga que la operación que necesita protección.

**`LOCK TABLE mesas`.** Resuelve el problema y es peor: serializa **todas** las operaciones sobre esa mesa. Una lectura del detalle quedaría detrás de una unión, sobre una base donde casi nunca hay dos solicitudes a la vez.

**Pessimistic locking en la aplicación** (un `SELECT` y luego un `UPDATE` con la condición repetida). No agrega nada: el `UPDATE` con condición ya es atómico en PostgreSQL. El locking pesimista de aplicación solo tiene sentido sobre un motor donde el `UPDATE` no pueda ser condicional.

Las tres se descartan por la misma razón: **ubican la exclusión mutua en la base, donde la contención es alta, cuando la contención real es por mesa y la mayoría de las mesas no la tienen nunca.**

### 5.3 La doble barrera

La solución fue poner la exclusión donde la competencia existe — por mesa, y solo durante la sección crítica — y dejar la garantía definitiva en la base.

```text
Barrera 1 (Redis)    SET reserva:vacante:{mesa_id} 1 NX EX 60
                     -> si ya existe: 409 "otra solicitud se está procesando, reintentá"
                     -> no decide QUIÉN se une; reduce la competencia a un intento a la vez

Barrera 2 (Postgres) UPDATE mesas SET jugadores_actuales = jugadores_actuales + 1
                      WHERE id = %s AND jugadores_actuales < jugadores_max
                      RETURNING id
                     -> solo una transacción recibe fila; las otras reciben None -> 409 "cupo agotado"
```

`mesas_api/app/models/mesa.py:70-79`, con el `try`/`finally` de liberación en `mesas_api/app/controllers/solicitudes_controller.py:44-56`.

**El `WHERE` y el `SET` están en una sola sentencia.** Esa es toda la diferencia entre funcionar y no funcionar: PostgreSQL evalúa la condición con el lock de fila ya tomado, así que la segunda transacción ve el valor que la primera ya confirmó. No hay ventana porque no hay dos sentencias.

**Por qué dos barreras y no una.** La barrera 1 no es la garantía, es el rendimiento: reduce teóricamente N intentos concurrentes a 1, y así 9 de ellos reciben un `409` barato desde Redis en lugar de saturar el pool de PostgreSQL. La barrera 2 es la garantía: es la que impide la sobreventa, y funciona **aunque Redis esté caído**. La propiedad que busqué deliberadamente es que **la consistencia de datos no dependa de la caché**. Si mañana Redis se pierde, el sistema sigue siendo correcto; solo pierde rendimiento.

**El `finally` y el TTL.** El `finally` libera la clave incluso si `ocupar_vacante` lanza. El TTL de 60 s cubre el caso que el `finally` no puede: que el proceso muera entre `reservar()` y el `try`. Sin TTL, una mesa podía quedar bloqueada para siempre. Con TTL, se desbloquea sola en un minuto.

Lo que esta barrera **no** resuelve está declarado como brecha L4: si el TTL expira dentro de la sección crítica, un segundo llamador puede entrar. Como la barrera 2 sigue en pie, el defecto es de throughput y no de consistencia. Es la brecha correcta, porque está en la capa que no sostiene la garantía.

### 5.4 Idempotencia: el otro caso, distinto del de concurrencia

La concurrencia cubre "dos solicitudes simultáneas". La idempotencia cubre "**la misma** solicitud repetida": un reintento, una recarga de página, un doble clic. Son problemas distintos y una solución no cubre la otra.

Implementé tres niveles, en este orden:

1. **Redis** — `idem:solicitud:{key}`, TTL 24 h. Camino rápido, cubre el reintento inmediato.
2. **Base de datos** — `obtener_solicitud_por_key(mesa_id, usuario_id, idem_key)`. Cubre el caso en que Redis se reinició y la clave se perdió, que es exactamente el escenario en que un caché no puede ser la única garantía.
3. **Cacheo de la respuesta** — `guardar_resultado(idem_key, solicitud)` al crearla, para que un reintento devuelva **el mismo objeto**, no uno equivalente reconstruido.

El nivel 2 es el que más importa conceptualmente, y es donde está la brecha L3: **`solicitudes_uniones.idem_key` no tiene restricción `UNIQUE`**. La idempotencia funciona porque la barrera 1 serializa los intentos, pero si dos procesos compiten con la misma clave y la barrera 1 ya venció, podrían insertar dos filas. La restricción `UNIQUE (mesa_id, usuario_id, idem_key)` convierte la garantía en una invariante de la base y es la primera corrección de AE4.

### 5.5 Evidencia

| Evidencia | Ubicación |
|---|---|
| Reproducción previa a la corrección | `tests/repro_carrera.py` |
| 10 concurrentes → 1×201 / 9×409 | `tests/test_carrera.py` |
| Captura antes/después | `AE2/evidencias/carrera_antes_despues.png` |
| Misma `Idempotency-Key` → cuerpo idéntico, `jugadores_actuales == 1` | `tests/test_idempotencia.py` |
| Decisión y alternativas descartadas | [ADR-004](../docs/ADR/ADR-004-doble-barrera.md) |

---

## 6. Redis: cuatro usos, cuatro políticas de expiración

El detalle está en §6 del informe conjunto. Lo que me corresponde fundamentar es la **distinción entre TTL e invalidación**, porque es la decisión de diseño de B04 y la que más se confunde.

### 6.1 Por qué la caché usa las dos

```text
cache-aside    GET cache:mesas:list
               miss -> SELECT -> SETEX 60
               hit  -> devolver

invalidación   POST /api/v1/mesas        -> DELETE cache:mesas:list
               PUT /api/v1/mesas/{id}    -> DELETE cache:mesas:list
               DELETE /api/v1/mesas/{id} -> DELETE cache:mesas:list
```

Son estrategias **complementarias, no alternativas**:

- La **invalidación** da corrección. Sin ella, un usuario que crea una mesa y recarga la lista ve la lista vieja.
- El **TTL** da seguridad. Si una invalidación se olvida, el dato no envejece de forma indefinida: en 60 segundos se corrige solo.

Elegir una sola tiene un costo explícito. Solo TTL → el usuario ve hasta 60 s de datos viejos, y 60 s es una demora perceptible en una aplicación donde acaba de crear algo. Solo invalidación → si una escritura nueva olvida la invalidación, el error es **permanente**, y no hay red que lo detecte.

El precio de esta estrategia es que **hay que recordar la invalidación en cada escritura**, y está declarado como consecuencia negativa en [ADR-002](../docs/ADR/ADR-002-redis.md). Lo acepté porque el modo de fallo del olvido (datos viejos por un minuto) es mucho menos grave que el de la alternativa (datos viejos para siempre).

### 6.2 La sesión, que sí se invalida por evento

`sesion:{jti}` con TTL 86400 se elimina explícitamente en el logout. La diferencia con la caché es lanatureza del dato: una sesión vencida es un problema de seguridad, no una molestia de usabilidad, así que el TTL es la red de seguridad y el evento es la garantía.

### 6.3 El QR, donde expirar no es lo mismo que consumir

El caso que ilustra por qué "Redis con TTL" no es una técnica sino cuatro técnicas distintas:

```text
SETEX qr:{sesion}:{usuario} 600   ->  emisión
GETDEL qr:{sesion}:{usuario}      ->  validación
```

Un QR con TTL de 10 minutos sigue siendo válido durante esos 10 minutos **aunque ya se haya escaneado**. La expiración responde "¿este QR sigue siendo de este momento?", no "¿este QR ya se usó?". La segunda pregunta necesita un borrado atómico al leer, y ese es `GETDEL`, que además resuelve la concurrencia: dos validaciones simultáneas del mismo QR no pueden pasar ambas.

### 6.4 La reserva, donde `NX` es lo que la hace un candado

`SETNX` es lo que da atomicidad. `GET` seguido de `SET` no lo daría, porque entre ambos otro proceso puede escribir. El TTL de 60 s es la red de seguridad del proceso muerto (§5.3).

---

## 7. Integraciones y artefactos

### 7.1 QR de asistencia: por qué HMAC y no JWT

El sistema ya usaba JWT para las sesiones, así que la decisión obvia era réutilizarlo para el QR. No lo hice, y la razón es que **el QR no necesita ser autocontenido**.

La validación consulta la clave en Redis con un `GETDEL`. El `GETDEL` ya lee la clave, ya verifica que exista y ya la consume. Un JWT habría que verificarlo **y** además verificar que exista la clave: dos operaciones donde una alcanza. La firma HMAC queda entonces con una función acotada y clara: **detectar manipulación**, no autenticar. Si el GM pierde la clave, la validación falla con `400` en vez de devolver un `false` ambiguo.

El payload es `{sesion, u, exp}` en base64url, **sin datos personales** — ni email, ni nombre. Un QR se fotografía, se reimprime, se comparte; no debería llevar información identificable. La consecuencia negativa que acepté es que la firma no se puede verificar offline, y por eso la validación requiere Redis. Está en [ADR-007](../docs/ADR/ADR-007-qr-single-use.md).

### 7.2 PDF asíncrono: el `documento_id` lo genera el emisor

```text
POST /api/v1/builds/{id}/pdf  -> 202 { documento_id }
     el emisor genera el uuid4().hex
     publica doc.pdf.build
notif_api/app/workers/pdf.py  -> renderiza con fpdf2, documentos.estado = 'listo' | 'error'
GET /api/v1/pdf/{id}          -> application/pdf
```

La decisión con más consecuencias fue **quién genera el identificador**. Si lo generara el consumidor, el cliente no tendría nada que consultar hasta que el mensaje recorriera la cola, y la respuesta al `POST` no podría contener un identificador útil. Generándolo el emisor, el `202` es accionable desde el primer instante.

El otro punto es el fallo en el render: marca `estado = 'error'` y **relanza** la excepción (`workers/pdf.py:30-32`), que es lo que permite que el mecanismo de reintentos de §4.2 actúe. Un fallo capturado y solo registrado habría dejado el documento en `en_proceso` para siempre — el peor de los tres estados, porque no dice ni que falló ni que va a pasar algo.

### 7.3 Email con outbox: por qué `enviar_email` nunca lanza

```text
registrar fila en emails (outbox), estado = 'pendiente'
enviar por SMTP con SMTP_TIMEOUT = 3 s
actualizar estado = 'enviado' | 'fallido'
nunca propagar la excepción
```

Tres decisiones encadenadas:

**Nunca propaga.** Si el envío fallara y la excepción llegara al consumidor, el mensaje se reintentaría con backoff hasta la DLQ, y el usuario vería su unión revertida porque un servidor de correo estaba caído. Con el outbox, el email es un efecto registrado con un estado, no una precondición del negocio.

**Timeout de 3 segundos.** Sin él, un SMTP colgado bloquea el hilo del consumidor indefinidamente. El sandbox MailHog detenido se convierte en un cuelgue silencioso.

**Reintento manual expuesto.** `POST /api/v1/emails/{id}/reintentar` (solo admin) convierte un fallo en una operación recuperable sin intervención automática. El endpoint existe, el admin existe, y `tests/test_notif_auth.py` cubre que un usuario normal no lo alcance.

Consecuencia: MailHog es en memoria, así que los emails no sobreviven a un reinicio. Declarado como compromiso asumido. El patrón de outbox es lo que se conserva al cambiar de transporte.

### 7.4 Recuperación de contraseña sin enumerar cuentas

`POST /api/v1/auth/recuperar` responde **siempre** `{"ok": true}` (`notif_api/app/routes/v1/auth.py:18`), exista o no la cuenta.

El razonamiento: si la respuesta distinguiera entre "email no registrado" y "email enviado", el endpoint sería un oráculo de qué emails tienen cuenta. El costo es que un usuario con un typos no puede saberlo por la respuesta; se resuelve en el contenido del email que recibe. Es un intercambio correcto: la enumeración de cuentas es una vulnerabilidad de privacidad y el typos es una molestia.

---

## 8. Seguridad y observabilidad

### 8.1 Sesión revocable

```text
login    -> access_token + refresh_token
        -> SETEX sesion:{jti} 86400
        -> el middleware valida sesion_valida(jti) en CADA request autenticado
logout   -> DEL sesion:{jti}    revocación inmediata
```

Un JWT sin registro en Redis es criptográficamente válido hasta que expira: el logout sería una mentira. El registro en Redis es lo que hace la revocación real, y por eso `sesion_valida(jti)` se consulta en **cada** request autenticado y no solo en el logout.

`usuario_actual` distingue cuatro casos de `401` — sin header, token inválido, refresh usado como access, sesión revocada — y `requerir_roles` devuelve `403`. La distinción importa: un `403` para un usuario sin permisos y un `401` para una sesión expirada llevan a comportamientos distintos en el cliente.

| Superficie | Rol | Archivo |
|---|---|---|
| Abrir matchmaking | `gm` | `mesas_api/app/routes/v1/matchmaking.py:10` |
| Validar QR | `gm` | `mesas_api/app/routes/v1/sesiones.py:19` |
| Event-log | `admin` | `notif_api/app/routes/v1/event_log.py:11` |
| Emails + reintento | `admin` | `notif_api/app/routes/v1/emails.py:12,15,20` |
| DLQ: ver / reintentar / descartar | `admin` | `notif_api/app/routes/v1/dlq.py:8,11,16,24` |

`tests/test_auth_registro_rol.py:29-54` verifica que el registro público nunca pueda escalar a `gm` ni a `admin`.

### 8.2 Correlación: el requisito que hay que pagar

`X-Correlation-Id` es lo que permite reconstruir un flujo que atraviesa tres procesos:

```text
HTTP X-Correlation-Id: cid-ev-2026-09-26-7f3a
 -> log JSON de mesas_api
 -> viaja DENTRO del cuerpo del evento   (app/infra/rabbitmq.py:30)
 -> el consumidor lo restaura a correlation_id_var  (_base.py:100)
 -> log JSON de notif_api
```

Que viaje **en el body del evento** y no en un header AMQP es lo que lo hace funcionar: el mensaje se consume en un hilo distinto del que lo publicó, y un `contextvar` de Python no sobrevive al salto de proceso. `correlation_id_var.set(cid)` y su `reset()` en el `finally` (`_base.py:103,139`) son la traducción explícita.

La brecha L7 es que este tramo no se cierra en la llamada `notif_api → mesas_api` (el `GET /miembros` no propaga el header). El tramo principal sí funciona, y es el que se evidencia con `AE2/evidencias/logs_correlation_id.png`.

### 8.3 Por qué `/live` y `/ready` están separados

```text
GET /live   -> 200 siempre
GET /ready  -> 200 listo | 503 degradado, con el detalle de dependencias
```

Un único endpoint de salud que consulta la base tiene un modo de fallo peligroso: si la base cae, el liveness probe falla, el orquestador reinicia el proceso, y al volver a levantar encuentra la base todavía caída, así que reinicia otra vez. El proceso entra en un ciclo de reinicios justo cuando lo que necesita es esperar.

Separarlos permite que `/live` responda "estoy vivo" sin mirar nada, y que solo `/ready` reporte `degradado` cuando una dependencia no está. La evidencia de los dos casos está en `AE2/evidencias/ready_live.png` (los cuatro servicios en `listo`) y `AE2/evidencias/ready_degradado.png` (`notif-api` en `degradado` con `redis: false` tras pausar Redis), y el comportamiento está en `tests/test_ready_degradado.py`.

---

## 9. Testing

### 9.1 Lo que la suite cubre y lo que no

130 pruebas de backend: 50 unitarias y 80 de integración. El inventario completo está en [`docs/testing/test-inventory.md`](./testing/test-inventory.md).

El reparto no es caprichoso: los 50 tests unitarios cubren lo que se puede verificar sin infraestructura (envelope, contratos de esquema, correlación, idempotencia de función pura), y los 80 de integración cubren lo que **solo** aparece con servicios reales —_AMQP, carreras de verdad, TTLs, DLQ. Un mock de RabbitMQ no habría detectado el defecto D-05, porque un binding faltante es una propiedad de la topología del broker, no de la API del cliente.

### 9.2 El aislamiento del broker, que salió de un defecto

`tests/conftest.py:25-35,124-151` aísla las pruebas de integración en el **vhost `/tfinder_test`**, no en el vhost raíz.

El motivo es concreto y lo registré como el defecto D-06: los contenedores `notif-api` del ambiente de desarrollo tienen consumidores suscritos a `notif.mesa`. Con un vhost compartido, esos consumidores stealing los mensajes de test, los procesaban, los rebotaban y terminaban publicando en la `dlq.general` del ambiente de desarrollo. El síntoma era una DLQ de desarrollo llenándose de basuraproduced por tests, y tests que fallaban de forma intermitente según el estado del ambiente.

La lección de proceso: **el aislamiento de los tests no es una formalidad, es parte del diseño**, y aquí se encontró por un fallo, no por pensar. El fixture se acompaña de un `autouse` (`conftest.py:190-216`) que hace que cualquier test **unitario** que intente publicar en el broker real levante `AssertionError`, para que una fuga similar no pueda pasar inadvertida.

### 9.3 Los 9 defectos encontrados y corregidos

La verificación E2E ejecutó 99 casos HTTP. Los 9 defectos y sus regresiones están en [`docs/testing/integration-results.md`](./testing/integration-results.md). Los tres con valor arquitectónico ya están comentados: **D-04** (divergencia del envelope), **D-05** (DLX sin binding) y **D-02** (forma del campo `enlace` inconsistente entre la fila y el payload SSE).

Los demás fueron D-01 (404 que se convertía en 500 al abrir matchmaking de una mesa inexistente), D-03 (loop infinito en un test de DLQ), D-06 (contaminación del broker de desarrollo), D-07 (feed sin parámetros de consulta), D-08 (`conftest` sin las variables de base de builds y feed) y D-09 (cuelgue de AMQP → `pytest-timeout`).

Que 9 de 99 casos Finds defects es el resultado esperado de una integración real, no un síntoma de mala calidad. Lo importante es que cada uno tiene un test de regresión que lo faça fallar si vuelve.

### 9.4 Dos defectos de la propia suite

Al verificar la reproducibilidad de B11 aparecieron dos problemas **en la suite**, distintos de los 9 del producto.

**La suite entera fallaba al collectionarse.** `tests/conftest.py:134` usaba `pytest.warn(...)`, que no existe; la API correcta es `warnings.warn(...)`. Como `vhost_de_pruebas` es `autouse` de scope de sesión, el `AttributeError` abortaba el setup de los 130 tests. El bug estaba en la rama de degradación elegante —cuando la management API del broker no responde— que es justo el escenario en que uno espera que la suite **degrade y funcione**. Por eso pasó inadvertido: solo se manifiesta cuando el broker está caído, y en ese momento el síntoma que se observa es "no funciona", no "está mal escrito".

```python
pytest.warn("...", RuntimeWarning)    # antes  -> AttributeError
warnings.warn("...", RuntimeWarning)  # despues
```

**Un test `unit` que dependía de PostgreSQL.** `test_no_se_altera_una_respuesta_correcta` consultaba `/health`, que hace `SELECT 1`. Marcado como `unit`, el job `backend-unit` de CI —sin service containers, a diferencia de `backend-integration`— lo ejecutaría sin base y fallaría. Lo cambié a `/live`, que responde `200` sin tocar PostgreSQL y verifica la misma propiedad: que el middleware de errores no altera una respuesta correcta.

Los dos son la misma clase de problema: **nadie ejecutó la suite en el escenario en que falla**. Sin Docker levantado, el primero aborta todo y el segundo falla por falta de base. Es la clase de defecto que el fixture de aislamiento no cubre, porque protege contra la contaminación del ambiente pero no contra sus propias dependencias.

### 9.5 Brechas declaradas

Las cuatro están en `docs/testing/test-inventory.md`. La más relevante es la ausencia de E2E en navegador: la verificación E2E se hizo por HTTP, lo que cubre los contratos pero no el DOM. Se acepta y se declara.

---

## 10. Fundamentación: las siete decisiones

Los ADR están en `docs/ADR/`, cada uno con Contexto, Decisión y Consecuencias (positivas y negativas). Este es el índice con el razonamiento en una línea:

| # | Decisión | Alternativa descartada | Por qué |
|---|---|---|---|
| [ADR-001](../docs/ADR/ADR-001-postgres.md) | PostgreSQL 16, base por servicio | SQLite (AE1) | SQLite serializa las escrituras: no hay forma de probar concurrencia. Un sistema cuyo problema central es la carrera necesita una base donde la carrera exista |
| [ADR-002](../docs/ADR/ADR-002-redis.md) | Caché con invalidación **y** TTL | Solo TTL | Solo TTL deja 60 s de datos viejos; solo invalidación hace el olvido permanente. Las dos juntas, cada una cubriendo el fallo de la otra |
| [ADR-003](../docs/ADR/ADR-003-rabbitmq.md) | ACK + reintentos en el body + DLQ | `nack(requeue=True)` | Reencolar la copia original pierde los headers y el contador nunca avanza: el mensaje vuelve para siempre |
| [ADR-004](../docs/ADR/ADR-004-doble-barrera.md) | Doble barrera Redis + Postgres | `FOR UPDATE`; `LOCK TABLE` | El lock de fila dura toda la transacción y ocupa un slot del pool; `LOCK TABLE` serializa además las lecturas |
| [ADR-005](../docs/ADR/ADR-005-mailhog-outbox.md) | Outbox, nunca propaga | Propagar la excepción | Un SMTP caído reintentaría en loop y, si el error se propagara, haría fallar una unión de usuario por un email |
| [ADR-006](../docs/ADR/ADR-006-servicios.md) | 4 servicios, cero SQL cruzada | Base compartida con esquema común | Un esquema común hace que "no leer datos ajenos" dependa de la disciplina, no de la estructura |
| [ADR-007](../docs/ADR/ADR-007-qr-single-use.md) | HMAC + payload mínimo + `GETDEL` | JWT para el QR | El `GETDEL` ya lee, verifica y consume. Un JWT exigiría verificar firma **y** existencia sin ganar nada |

### 10.1 El criterio que comparten las siete

Todas se elegiron por **lo que ocurre cuando fallan**, no solo por lo que hacen cuando funcionan:

- El `finally` de la barrera → para el caso en que la operación falla.
- El TTL de 60 s en la reserva → para el caso en que el proceso muere antes del `finally`.
- La DLQ → para el caso en que un mensaje no se puede procesar nunca.
- El outbox y su `nunca lanza` → para el caso en que un componente externo no responde.
- La separación lógica de bases → para que la consistencia no dependa de que nadie cometa un error.
- La doble barrera → para que la consistencia no dependa de que Redis esté disponible.

La pregunta que usé como filtro fue: *¿qué pasa si este componente no está disponible?* La respuesta, en los siete casos, es que ninguna parte de la consistencia de datos depende de Redis ni de RabbitMQ, y ambos son recuperables por diseño. Esa es la propiedad que hace que el sistema pueda seguir operando cuando una de sus piezas se cae, y es lo que verifiqué con las evidencias de `ready_degradado.png`.

---

## 11. Limitaciones de mi alcance

De las 12 limitaciones del informe conjunto (§13), estas son las de mi parte. Las declaro porque un informe que se presenta sin brechas no es verificable.

| # | Limitación | Impacto | Mitigación |
|---|---|---|---|
| L1 | Sin outbox transaccional: `publicar()` fuera de la transacción (`solicitudes_controller.py:53`) | Si el broker cae tras el commit, el evento se pierde | Outbox transaccional en AE4 |
| L3 | Sin `UNIQUE` en `solicitudes_uniones.idem_key` | La idempotencia depende de la barrera 1, no de una restricción | `UNIQUE (mesa_id, usuario_id, idem_key)` — primera corrección de AE4 |
| L4 | Barrera 1 sin fencing token | Si el TTL vence dentro de la sección crítica, entra un segundo llamador | La barrera 2 sigue impidiendo la sobreventa: es brecha de throughput, no de consistencia |
| L5 | PDF sin volumen Docker | Los PDF se pierden al recrear `notif-api` | Montar un volumen en AE4 |
| L6 | Reintento de DLQ no atómico (`dlq.py:11-28`) | Se borra la fila y luego se publica; un fallo pierde el mensaje | Afecta a la operación manual de admin; outbox también aquí |
| L7 | `correlation_id` no propagado en `notif → mesas` | La traza se corta en ese tramo | El tramo principal request → evento → consumidor sí funciona; se completa en AE4 |
| L8 | `sesion.confirmada` y `sesion.diario_publicado` sin productor | El consumidor `notif.sesion` no es alcanzable desde un endpoint | Faltan los endpoints de confirmación de sesión |
| L12 | 4 copias del middleware JWT, una por servicio | Cualquier cambio se replica 4 veces | Hoy son idénticas; extraer a `app/` cuando el segundo servicio necesite modificarlo |
| — | `init_db()` sin lock ni herramienta de migraciones | Con varias réplicas podrían competir al arrancar | Hoy inofensivo: el DDL es idempotente (`IF NOT EXISTS`) |
| — | `python-json-logger` instalado y sin usar | Dependencia muerta | El formateo JSON es propio en `app/infra/logge.py` |

**Ninguna de estas afecta la consistencia de los datos.** Las que afectan corrección —L1 y L3— están ambas en la ruta natural de AE4, y L3 es una restricción de una línea.

---

## 12. Trazabilidad individual

### 12.1 Rama, commits e issues

```bash
git log --oneline 1781e4e..AE2-Backend              # 79 commits
git log --format='%h %s' 1781e4e..AE2-Backend | grep '#[0-9]*'   # los 12 issues
git diff --stat 1781e4e..AE2-Backend -- app/ mesas_api/ builds_api/ feed_api/ notif_api/ docs/
```

Cada commit de B01–B12 sigue el formato Conventional Commits en español con el issue asociado:

```text
f892f7d  feat(infra): docker compose con postgres/redis/rabbitmq/mailhog (#14)
8dae133  refactor(backend): separacion en 4 servicios (mesas/builds/feed/notif) con Postgres (#15)
3dd0272  feat(mesas-api): autenticacion JWT con sesiones en Redis (#16)
6395191  feat(mesas-api): cache y estado efimero en Redis con TTL (#17)
6a70869  feat(notif): eventos RabbitMQ con DLQ e idempotencia (#18)
6610e3d  feat(mesas): doble barrera e idempotencia por key (#19)
29058f6  feat(mesas): QR de asistencia single-use con HMAC y GETDEL (#20)
20b6849  feat(builds): PDF asincrono con 202 y worker (#21)
756b3f9  feat(notif): email con outbox y timeout SMTP (#22)
9f10f66  feat(observabilidad): logs JSON, correlation-id, /live y /ready (#23)
47008b6  test: suite de pruebas unitarias e integración (#24)
834af06  docs(ae2): ADRs, OpenAPI verificado, evidencias por criterio y README de entrega (#25)
```

El historial es lineal y sin ambigüedad de autoría porque el trabajo de backend se hizo íntegramente en `AE2-Backend` antes de la integración. Los 90 commits de la rama `AE2-Testing` incluyen los 79 de esta rama más la integración y el testing.

### 12.2 OpenSpec como trazabilidad de tareas

Cada bloque B01–B12 tiene un cambio en `openspec/changes/` con `proposal.md` y `tasks.md`, y su capacidad publicada en `openspec/specs/`. Los `tasks.md` permiten reconstruir el trabajo con granularidad de tarea, y cada requirement de las specs está en formato GIVEN/WHEN/THEN, lo que hace que cada comportamiento sea verificable.

**Estado de cierre administrativo:** la implementación de los 12 bloques está completa y verificada, pero los pasos administrativos finales —archivar el cambio en OpenSpec y cerrar el issue— están marcados como pendientes en varios `tasks.md`. Lo dejo declarado en lugar de marcar en verde algo que no ejecuté: `docs/AUDITORIA_CIERRE_AE2.md` §8 lista los 12 puntos de cierre, y la integración con la cátedra queda a lo que determine AE4.

### 12.3 Evidencias

| Evidencia | Criterio | Archivo |
|---|---|---|
| Redis: TTL e invalidación | 6 | `redis_ttl.png` |
| RabbitMQ: colas y DLQ | 5 | `rabbit_colas_y_dlq.png` |
| Carrera de la última vacante | 7 | `carrera_antes_despues.png` |
| Email en MailHog | 9 | `email_mailhog.png` |
| QR de un solo uso | 9 | `qr_single_use.png` |
| PDF asíncrono `202` → `200` | 9 | `pdf_202_y_ficha.png` |
| Logs con `correlation_id` en 2 servicios | 8 | `logs_correlation_id.png` |
| Event-log por `correlation_id` | 8 | `event_log_correlation.png` |
| SSE en vivo | 8 | `sse_notificaciones.png` |
| `/ready` en los 4 servicios | 13 | `ready_live.png` |
| `/ready` degradado con Redis caído | 13 | `ready_degradado.png` |
| DLQ: reintentar y descartar | 9 | `dlq_reintentar_y_descartar.png` |

Todas en `AE2/evidencias/`, indexadas en [`EVIDENCIAS.md`](../AE2/evidencias/EVIDENCIAS.md) y regenerables con `python scripts/generar_evidencias.py`.

---

## 13. Conclusión

Mi alcance en AE2 fue llevar el backend de TFinder de un monolito CRUD sobre SQLite a un sistema de cuatro servicios con contratos REST, mensajería asíncrona, estado efímero en Redis y una base por servicio, resolvió de forma demostrable la carrera por la última vacante, y dejó el sistema con evidencia reproducible de su comportamiento.

Lo que más rescato del proceso, en orden de valor:

**La disciplina de reproducir el defecto antes de corregirlo.** `tests/repro_carrera.py` se escribió antes que la doble barrera. Sin esa disciplina, la corrección habría sido "agregar un lock" sin poder demostrar que el problema existía ni que la solución lo resolvía.

**La doble barrera, y sobre todo la propiedad de que la consistencia no depende de la caché.** Elegir Redis para la exclusión mutua fue una decisión de rendimiento; elegir que PostgreSQL sea la garantía fue una decisión de diseño. Si mañana Redis desaparece, el sistema sigue siendo correcto.

**Que los contratos se verificaran, no se declararan.** El piso de rutas, la identidad de los manejadores de error compartidos, la property ownership con un `rg` que lo comprueba, y el binding del DLX verificado por management API: cuatro invariantes que se pueden romper sin que nadie lo note si no están escritas como test o como comando.

**Que los 9 defectos se hallaran por integración real.** D-04 y D-05 no eran visibles leyendo el código de un servicio. Aparecieron cuando hubo dos servicios hablando y un broker real. La lección es que un contrato entre servicios no existe hasta que se verifica en ejecución.

Las limitaciones de §11 están declaradas con su impacto. Ninguna afecta la consistencia de los datos, y las dos que sí afectan corrección están en la ruta de AE4.
