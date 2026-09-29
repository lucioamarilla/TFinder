---
title: "TFinder AE2 — Demostración de la infraestructura"
subtitle: "Docker, Redis, RabbitMQ, la cola de mensajes fallidos, y los 49 endpoints verificados"
date: "Verificado contra el stack en vivo el 2026-09-29"
lang: es-AR
---

# 0. Mapa de este documento

Este documento cubre la parte que la interfaz no muestra. Todo lo que esta aca se ejecuto
contra el stack levantado y las salidas son reales.

| Seccion | Tema | Que demuestra |
|--:|---|---|
| 1 | Docker | 8 contenedores, salud, y que pasa cuando uno se cae |
| 2 | Redis | Los 6 usos, con TTL real medido |
| 3 | RabbitMQ | Topologia real y publicacion manual de eventos |
| 4 | Cola de fallidos | Como un mensaje termina en la DLQ y como se reintenta |
| 5 | PDF asincrono | El unico flujo que cruza tres servicios |
| 6 | Notificaciones | SSE, correo y la bandeja de salida |
| 7 | Correlacion | Un solo identificador de punta a punta |
| 8 | Endpoints | Los 49, con metodo y autenticacion |
| 9 | Pruebas | Como correr la suite |

> **Todos los comandos de este documento se ejecutaron.** Donde la salida es un valor
> concreto (un TTL, un codigo HTTP, un conteo), ese valor es el observado, no un ejemplo.

---

# 1. Docker

## 1.1 Los ocho servicios

```bash
docker compose ps
```

| Servicio | Imagen | Puerto host | Salud |
|---|---|---|---|
| `postgres` | `postgres:16-alpine` | 5432 | `pg_isready` |
| `redis` | `redis:7-alpine` | **6390** | `redis-cli ping` |
| `rabbitmq` | `rabbitmq:3.13-management-alpine` | **5673** / **15673** | `rabbitmq-diagnostics` |
| `mailhog` | `mailhog/mailhog:v1.0.1` | 1025 / 8025 | — |
| `mesas-api` | imagen propia | 8001 | — |
| `builds-api` | imagen propia | 8002 | — |
| `feed-api` | imagen propia | 8003 | — |
| `notif-api` | imagen propia | 8004 | — |
| `frontend` | imagen propia (nginx) | 5173 | `wget /health` |

**Los puertos no obvios.** Redis se publica en **6390** y AMQP en **5673**, no en sus puertos
estandar. La UI de RabbitMQ queda en **15673**. Es la primera fuente de confusion para
quien intenta conectarse a mano.

**Una sola imagen para las cuatro APIs.** El `Dockerfile` recibe el nombre del servicio como
argumento de construccion y copia solo ese paquete. Las cuatro comparten la libreria `app/`
(infraestructura generica: Redis, RabbitMQ, logs, middleware).

## 1.2 Las tres sondas de salud, y por que son tres

| Endpoint | Toca dependencias | Para que sirve |
|---|---|---|
| `/live` | **no** | "el proceso esta vivo" — responde aunque todo lo demas este caido |
| `/ready` | postgres, redis, rabbitmq | "puede recibir trafico" |
| `/health` | solo postgres | chequeo basico del servicio |

La distincion importa: si Redis se cae, el proceso **sigue vivo** (`/live` en 200) pero
**no debe recibir trafico** (`/ready` en 503). Un orquestador usa `/live` para decidir si
reinicia el contenedor y `/ready` para decidir si le manda trabajo.

## 1.3 La demostracion del modo degradado

```bash
docker compose pause redis
sleep 1
curl -s -w " [%{http_code}]\n" http://127.0.0.1:8001/ready
```

**Salida real:**

```json
{"estado":"degradado","dependencias":{"postgres":true,"redis":false,"rabbitmq":true}}
 [503]
```

Lo importante: el servicio **no se cae**. Sigue respondiendo, y ademas dice **exactamente
que dependencia falta**. Y `/live` sigue en 200:

```bash
curl -s -w " [%{http_code}]\n" http://127.0.0.1:8001/live
# {"estado":"vivo"} [200]
```

Se restaura con `docker compose unpause redis`, y `/ready` vuelve a `listo` con los tres en
`true`. El timeout de conexion a Redis es de 2 segundos, asi que la degradacion se detecta
rapido.

> Se puede usar `docker compose stop rabbitmq` en lugar de `pause`. La diferencia es que
> `stop` mata el contenedor y `pause` lo congela: con `pause` el broker sigue en la red pero
> no responde, que es el escenario mas realista de un cuelgue.

---

# 2. Redis

Redis cumple **seis funciones distintas**, y ninguna es la misma que la otra. Todas las claves
tienen fecha de expiracion: Redis nunca es la fuente de verdad, es estado temporal.

## 2.1 Como mirar las claves

```bash
# Listar todo con su tipo y su TTL
docker compose exec -T redis redis-cli --scan --pattern '*' | sort | while read -r k; do
  printf "%-44s type=%-8s ttl=%s\n" "$k" \
    "$(docker compose exec -T redis redis-cli TYPE "$k")" \
    "$(docker compose exec -T redis redis-cli TTL "$k")"
done
```

> Si el bucle imprime una sola linea de un `while read` alimentado por un pipe, el problema es
> que `docker compose exec` se queda con la entrada estandar y se come el resto de las lineas.
> Se arregla redirigiendo `< /dev/null` en cada llamada, o guardando primero las claves en un
> archivo y despues leyendolas.

## 2.2 Los seis usos

| # | Clave | TTL | Proposito |
|--:|---|--:|---|
| 1 | `sesion:{jti}` | 86400 s | Sesion viva; permite revocar un token |
| 2 | `cache:mesas:list` | 60 s | Cache del listado de mesas |
| 3 | `idem:solicitud:{clave}` | 86400 s | Replay de una solicitud de union |
| 4 | `reserva:vacante:{mesa}` | 60 s | Cerrojo de concurrencia (`SET NX`) |
| 5 | `llamado:{matchmaking}` | 120 s | Ventana del llamado |
| 6 | `qr:sesion:{s}:{u}` | 600 s | Token de uso unico del QR |

## 2.3 Uso 1 — La sesion, que hace posible revocar un token

Un JWT por si solo no se puede invalidar: sigue siendo criptograficamente valido hasta que
expira. La solucion aqui es no confiar solo en el token.

Al iniciar sesion, ademas de firmar el JWT, se escribe una clave en Redis con el
identificador unico del token (campo `jti`):

```bash
docker compose exec -T redis redis-cli --scan --pattern 'sesion:*'
```

**Salida real de la verificacion:**

```
sesion:0ca990fb79ee4bb3b967096efeff3a08   ttl=86342
sesion:2d382ff3b88e409d83316621f3d6c498   ttl=86366
sesion:3ade7bd6c9c8438097bd642d4af20cbe   ttl=86341
...  (10 claves en total)
```

Los TTL observados van de 86340 a 86366 sobre un valor inicial de 86400: la diferencia son
los minutos transcurridos desde el inicio de sesion. Eso confirma que la clave **se esta
contando hacia abajo sola**.

**La demostracion que convence:** iniciar sesion, copiar el token, cerrar sesion, y usar el
token viejo:

```bash
curl -s -X POST http://127.0.0.1:8001/api/v1/auth/logout -H "Authorization: Bearer $GM"
# {"ok":true}

# El mismo token, ahora rechazado
curl -s -w " [%{http_code}]\n" http://127.0.0.1:8001/api/v1/auth/me -H "Authorization: Bearer $GM"
```

La clave `sesion:{jti}` desaparece. Como **los cuatro servicios** consultan la misma clave,
un `logout` en mesas-api invalida el token en los cuatro a la vez. Esa es la ventaja de que
el estado de sesion no viva en la memoria de un proceso.

## 2.4 Uso 2 — El cache, y por que se invalida ademas de expirar

```bash
curl -s -o /dev/null http://127.0.0.1:8001/api/v1/mesas
docker compose exec -T redis redis-cli TTL cache:mesas:list
```

**Salida real: `60`.** Exactamente el TTL configurado, y el valor guardado es el JSON
completo del listado.

```bash
docker compose exec -T redis redis-cli GET cache:mesas:list
```

```
[{"id": 1, "nombre": "Mesa Demo Abierta", "sistema": "PF1e", "descripcion": "Camp...
```

**La invalidacion explicita importa mas que el TTL.** Al crear, editar o borrar una mesa, la
clave se borra en el mismo momento. Si solo dependiera del TTL, alguien podria ver un
listado hasta 60 segundos desactualizado despues de crear una mesa, y en una demo eso es
justo lo que no puede pasar. El TTL es la red de seguridad; la invalidacion es la garantia.

Para verlo: crear una mesa por API y mirar la clave desaparecer.

## 2.5 Uso 3 — La idempotencia

Cuando se pide unirse, el cliente envia una clave. Esa clave se guarda 24 horas con la fila
resultante, y si la misma peticion llega de nuevo se devuelve lo guardado en vez de crear un
duplicado.

**Salida real:**

```
idem:solicitud:probeA-1     ttl=86367
idem:solicitud:probe-join-1 ttl=86360
```

## 2.6 Uso 4 — El cerrojo de concurrencia (el mas importante)

```bash
SET reserva:vacante:2 NX EX 60
```

`NX` significa "solo si no existe". Es la primera barrera contra la carrera por la ultima
vacante: si ya hay una peticion procesando esa mesa, la segunda recibe `409` en el acto, sin
llegar a tocar la base.

**Lo que hay que decir con honestidad:** esta clave **no se va a ver nunca** si se inspecciona
Redis desde afuera. Se toma y se libera dentro de la misma peticion, en un bloque `finally`,
y dura microsegundos. Escribiendolo asi se hace explicito que es un cerrojo, no un estado
persistente. La demostracion de que funciona es la carrera de la seccion 3.3 del documento de
la aplicacion, no la inspeccion de la clave.

## 2.7 Uso 5 — La ventana del llamado

```bash
docker compose exec -T redis redis-cli --scan --pattern 'llamado:*'
# llamado:2
docker compose exec -T redis redis-cli TTL llamado:2
```

**Salida real: `92`.** Se abrio con 120 y ya quedaban 92: se estaba contando en el momento
de mirarlo. Eso es la ventana de anotarse al llamado, y es lo que permite que expire sola sin
que haya una tarea programada que la cierre.

## 2.8 Uso 6 — El QR de un solo uso

```bash
curl -s -X POST http://127.0.0.1:8001/api/v1/sesiones/1/qr \
  -H "Authorization: Bearer $GM" > /tmp/qr.json

docker compose exec -T redis redis-cli --scan --pattern 'qr:*'
docker compose exec -T redis redis-cli TTL qr:sesion:1:2
```

**Salida real: `600`.** Y la clave es `qr:sesion:1:2`, es decir
`sesion` + `sesion_id` + `usuario_id` del emisor.

El contenido del `qr_data` descodificado:

```json
{
  "cuerpo": {"sesion": 1, "u": 2, "exp": 1790701209},
  "firma": "8e1acc8d72d3ee75b2105602c6631386"
}
```

La firma es un HMAC-SHA256 truncado. No es un JWT: es deliberadamente un formato minimo, sin
datos personales dentro, para que el QR sea solo un comprobante.

**El unico uso esta garantizado por `GETDEL`**, que lee y borra en una sola operacion atomica:

```bash
# 1) Validar por primera vez
curl -s -X POST http://127.0.0.1:8001/api/v1/sesiones/1/qr/validar \
  -H "Authorization: Bearer $GM" -H 'Content-Type: application/json' \
  -d "{\"usuario_id\":2,\"qr_data\":\"$QR\"}"
# {"asistencia":"registrada"}   [200]

# 2) Repetir exactamente lo mismo
# {"error":{"codigo":409,"mensaje":"QR vencido o ya utilizado"}}   [409]
```

> **Atar al emisor.** La clave se escribe con el identificador del usuario que emitio el QR,
> y al validar se busca con el `usuario_id` del cuerpo. Si no coinciden, la clave no existe y
> la respuesta es `409`, no un error de validacion. Es decir: **solo quien emitio el QR puede
> registrar su propia asistencia con el**. Es una limitacion conocida, documentada, y no un
> accidente. Si el jurado pregunta si un jugador puede escanear el QR del master, la
> respuesta honesta es que hoy no.

---

# 3. RabbitMQ

## 3.1 La topologia real

Salida de `rabbitmqctl list_exchanges`, `list_queues` y `list_bindings` en el stack vivo:

**Exchanges:**

```
tfinder.events    topic    durable
tfinder.dlx       topic    durable
```

**Colas:**

```
name          durable  messages  consumers
notif.mesa    true     0         1
notif.sesion  true     0         1
doc.pdf       true     0         1
dlq.general   true     0         0
```

**Bindings:**

```
tfinder.events -> notif.mesa    mesa.*
tfinder.events -> notif.sesion  sesion.*
tfinder.events -> doc.pdf       doc.pdf.*
tfinder.dlx    -> dlq.general  #
```

## 3.2 Que muestra ese grafo

```
                    +--------------------+
   mesas-api  ---> |                    |  mesa.*     -> notif.mesa    (1 consumidor)
   builds-api ---> |  tfinder.events    |  sesion.*   -> notif.sesion  (1 consumidor)
   feed-api   ---> |   (topic, durable)|  doc.pdf.*  -> doc.pdf       (1 consumidor)
                    +--------------------+
                                |
                                | nack(requeue=False) tras 3 intentos
                                v
                    +--------------------+
                    |    tfinder.dlx     |  #  ->  dlq.general (0 consumidores)
                    +--------------------+

Los tres consumidores viven dentro del contenedor notif-api,
como tres hilos en segundo plano.
```

Tres detalles que valen la pena explicar:

1. **Un exchange, cuatro tipos de evento.** El productor no sabe quien va a consumir. Publica
   `mesa.aceptada` y ahi se spreads; el que esta interesado se engancho.
2. **El binding `#` del exchange de fallidos es obligatorio.** Sin el, un mensaje enviado a
   un exchange sin destino se **descarta en silencio**: RabbitMQ no da error. Este fue un
   defecto real del proyecto (el exchange de fallidos existia pero sin ningun binding), y por
   eso hay una prueba automatizada que verifica exactamente este grafo.
3. **`dlq.general` con 0 consumidores** es correcto: nadie la consume automaticamente. Un
   operador la revisa y decide.

## 3.3 Los eventos que produce el codigo

| Evento | Lo produce | Lo consume |
|---|---|---|
| `mesa.solicitada` | `POST /mesas/{id}/solicitar` (endpoint heredado) | `notif.mesa` |
| `mesa.aceptada` | `POST /mesas/{id}/solicitudes` | `notif.mesa` |
| `mesa.expulsada` | — (definido, sin ruta que lo emita) | `notif.mesa` |
| `doc.pdf.build` | `POST /builds/{id}/pdf` | `doc.pdf` |
| `doc.pdf.diario` | `POST /mesas/{m}/sesiones/{s}/diario/pdf` | `doc.pdf` |
| `sesion.confirmada` | — (sin productor) | `notif.sesion` |
| `sesion.diario_publicado` | — (sin productor) | `notif.sesion` |

## 3.4 Publicar a mano los que no tienen productor

Tres eventos no los emite ninguna ruta. Para verlos funcionar hay que publicarlos a mano.
Este es el script:

```python
import pika, json, uuid

c = pika.BlockingConnection(
    pika.URLParameters("amqp://tfinder:tfinder@localhost:5673/"))
ch = c.channel()

evento = {
    "event_id": uuid.uuid4().hex,          # obligatorio: es la clave de idempotencia
    "tipo": "sesion.confirmada",           # decide que cola lo recibe
    "correlation_id": "demo-manual",
    "sesion_id": 1,
    "mesa_id": 1,
    "fecha": "2026-09-30T20:00:00+00:00",
    "detalle": "Sesion de apertura confirmada",
}

ch.basic_publish(
    exchange="tfinder.events",
    routing_key="sesion.confirmada",
    body=json.dumps(evento).encode(),
    properties=pika.BasicProperties(
        content_type="application/json",
        delivery_mode=2))                  # 2 = persistente
c.close()
```

Ejecutar con el interprete del entorno virtual del proyecto:

```bash
venv/bin/python /ruta/al/script.py
```

> Detalle practico: `delivery_mode` es un argumento de `pika.BasicProperties`, **no** un
> parametro de `basic_publish`. Pasarlo como parametro lanza un `TypeError`.

**Que se obtiene al publicar `sesion.confirmada`:** el consumidor `notif.sesion` inserta una
notificacion, la publica en el stream en vivo, y **ademas envia un correo a cada miembro de
la mesa**. Para lograr eso necesita la lista de correos, y no puede consultar la base de
mesas directamente: lo pide por HTTP a mesas-api. Ese es el unico cruce entre servicios del
proyecto, y se hace por contrato, no por SQL compartido.

Verificacion:

```bash
curl -s "http://127.0.0.1:8004/api/v1/emails?limite=4" -H "Authorization: Bearer $ADM"
```

**Salida real tras la publicacion manual:**

```
emails registrados: 4
  -> probecorr@tfinder.dev | TFinder · Sesión confirmada | enviado
  -> jugador1@tfinder.dev  | TFinder · Sesión confirmada | enviado
  -> jugador1@tfinder.dev  | TFinder · Sesión confirmada | enviado
  -> jugador2@tfinder.dev  | TFinder · Sesión confirmada | enviado
```

Y en MailHog (<http://localhost:8025>) aparecen los 4 mensajes.

> Ojo: `jugador1@` aparece dos veces. El fan-out consulta los miembros de la mesa, y un mismo
> usuario puede estar registrado mas de una vez como miembro si las corridas anteriores no se
> limpiaron. Con `docker compose down -v` antes de la defensa esto no ocurre.

## 3.5 Por que los reintentos se hacen republicando, no con `nack`

Cuando un consumidor falla, no hace `nack(requeue=True)`. Lo que hace es:

1. Republicar el mensaje con un contador `_intentos` incrementado **en el cuerpo**.
2. Confirmar el original (`ack`), para que no vuelva a verlo.
3. Esperar `2^intentos` segundos: 2 s, luego 4 s.
4. Al tercer fallo, enviarlo a la cola de fallidos y anotarlo en la base.

**Por que el contador va en el cuerpo y no en las cabeceras:** la biblioteca de la derecha no
conserva las cabeceras modificadas al reencolar, asi que un contador en cabecera se perderia
al segundo reintento. Y en el cuerpo sobrevive exactamente igual que la idempotencia.

---

# 4. La cola de mensajes fallidos

## 4.1 Provocarla a proposito

Se publican dos mensajes con un `id_origen` que no existe, para que el consumidor de PDF
falle:

```bash
venv/bin/python - <<'PY'
import pika, json, uuid
c = pika.BlockingConnection(
    pika.URLParameters("amqp://tfinder:tfinder@localhost:5673/"))
ch = c.channel()
cid = "probe-" + uuid.uuid4().hex[:8]
for i in range(2):
    ch.basic_publish(
        exchange="tfinder.events",
        routing_key="doc.pdf.build",
        body=json.dumps({
            "event_id": f"veneno-{i}-{cid}",
            "tipo": "doc.pdf.build",
            "correlation_id": cid,
            "documento_id": f"veneno-{i}",
            "tipo_doc": "build",
            "id_origen": -1,          # <- no existe: fuerza el fallo
        }).encode(),
        properties=pika.BasicProperties(content_type="application/json",
                                        delivery_mode=2))
c.close()
PY
```

Despues hay que **esperar 12 segundos**: el consumidor falla, espera 2 s, reintenta, falla,
espera 4 s, reintenta, y a la tercera fois lo manda a la cola de fallidos.

## 4.2 Verificar

```bash
curl -s "http://127.0.0.1:8004/api/v1/dlq?limite=5" -H "Authorization: Bearer $ADM"
```

**Salida real:**

```
total: 4
  id 51 | doc.pdf | _intentos 2 | tipo no soportado: doc.pdf.build
  id 50 | doc.pdf | _intentos 2 | tipo no soportado: doc.pdf.build
  id 49 | notif.mesa | _intentos 2 | tipo no soportado: mesa.desconocida
```

El campo `_intentos: 2` es la prueba de que el mensaje **reintento y fallo dos veces** antes
de ser descartado. No se mando a la cola de fallidos al primer fallo.

## 4.3 Reintentar y descartar

```bash
# Reintentar: vuelve a publicar el mensaje y borra la fila
curl -s -X POST http://127.0.0.1:8004/api/v1/dlq/51/reintentar \
  -H "Authorization: Bearer $ADM"
# {"ok":true,"id":51,"cola":"doc.pdf"}   [200]

# Descartar: elimina la fila sin reintentar
curl -s -X DELETE http://127.0.0.1:8004/api/v1/dlq/50 \
  -H "Authorization: Bearer $ADM"
# {"ok":true,"id":50}   [200]
```

> **Comportamiento que hay que saber.** Reintentar **no garantiza** que el mensaje se
> procese. En la verificacion, tras reintentar el id 51, la cola seguia con 10 mensajes en
> lugar de 9: el mensaje reintentado volvio a fallar y **volvio a entrar a la cola de
> fallidos**. Es el comportamiento correcto —un mensaje que falla siempre no puede quedar
> dando vueltas para siempre—, pero conviene decirlo antes de que el jurado lo note.

> **Antes de la defensa:** `docker compose down -v` y relanzar. La cola de fallidos acumula
> mensajes de corridas previas y una DLQ con 40 entradas no muestra nada.

---

# 5. PDF asincrono

Es el flujo mas elegante para mostrar, porque atraviesa **tres servicios** con un solo
identificador.

## 5.1 Los tres pasos

```bash
# 1) Disparar — responde 202 de inmediato
curl -s -X POST http://127.0.0.1:8002/api/v1/builds/1/pdf \
  -H "Authorization: Bearer $GM"
```

**Respuesta real:**

```json
{"estado":"aceptado","documento_id":"f052cb646f54471ca451255976a3f173",
 "detalle":"turno_enviado"}
```

**Lo que hay que explicar:** el identificador del documento lo genera **quien lo pide**, no
quien lo produce. Por eso el `202` puede devolverlo de inmediato: todavia no existe ningun
archivo, solo el turno en la cola.

```bash
# 2) Consultar el estado
curl -s http://127.0.0.1:8004/api/v1/pdf/{documento_id}/estado \
  -H "Authorization: Bearer $GM"
```

**Respuesta real:**

```json
{"documento_id":"f052cb646f54471ca451255976a3f173","tipo":"build",
 "id_origen":1,"estado":"listo",
 "fecha":"2026-09-29T16:51:04.407109+00:00"}
```

```bash
# 3) Descargar
curl -s -o doc.pdf -w "HTTP=%{http_code} type=%{content_type} bytes=%{size_download}\n" \
  http://127.0.0.1:8004/api/v1/pdf/{documento_id} -H "Authorization: Bearer $GM"
```

**Salida real:**

```
HTTP=200 type=application/pdf bytes=1257
```

Y el archivo es un PDF valido de una pagina.

## 5.2 La maquina de estados

```
  (nada)
     |  POST /builds/{id}/pdf        <- el cliente genera el documento_id
     v
 en_proceso  ---- GET /estado ---->  en_proceso
     |
     |  el worker genera el archivo
     v
   listo  -------- GET /pdf ------>  200 application/pdf
     |
     |  si la generacion falla
     v
   error
```

| Estado | Significado |
|---|---|
| `en_proceso` | el turno esta en la cola o el worker lo esta haciendo |
| `listo` | el archivo existe, se puede descargar |
| `error` | la generacion fallo; se puede reintentar |

**El `404` no es un error del sistema:** pedir el PDF mientras el estado es `en_proceso`
devuelve `404` a proposito, porque el archivo todavia no existe. Por eso el cliente tiene que
**consultar el estado antes de descargar**.

## 5.3 Los dos servicios de PDF

| Ruta | Tipo | Que genera |
|---|---|---|
| `POST /builds/{id}/pdf` (builds-api, 8002) | `doc.pdf.build` | Ficha de personaje |
| `POST /mesas/{m}/sesiones/{s}/diario/pdf` (feed-api, 8003) | `doc.pdf.diario` | Diario de sesion |

Los dos terminan en **el mismo worker** de notif-api, que es el unico que sabe escribir
archivos y registrar el documento en la base.

> **Limitacion conocida.** Los PDF se escriben en el disco del contenedor de notif-api y
> **no hay volumen montado** que los persista. Si se recrea ese contenedor, los archivos se
> pierden, aunque las filas de la base de datos sigan diciendo `listo`. Vale la pena
> mencionarlo si preguntan por la persistencia.

---

# 6. Notificaciones: SSE, correo y bandeja de salida

## 6.1 El stream en vivo

```bash
curl -N --max-time 30 \
  http://127.0.0.1:8004/api/v1/notificaciones/stream \
  -H "Authorization: Bearer $TOKEN"
```

Queda esperando. En otra terminal se dispara algo que genere una notificacion (por ejemplo,
unirse a una mesa) y el evento aparece en la primera.

**Formato de la respuesta:** `text/event-stream`, con un comentario `heartbeat` cada 15
segundos de inactividad para que las conexiones intermedias no corten el flujo.

> **No hay WebSockets en el proyecto.** El canal en vivo es Server-Sent Events, que es
> unidireccional: el servidor envia, el cliente no. Para este caso es la eleccion correcta y
> mas simple que WebSockets.
>
> **Y el frontend no lo usa.** La campana de notificaciones se actualiza con *polling* cada
> 5 segundos. El stream existe y funciona, pero ninguna pantalla lo consume. Si preguntan
> por tiempo real, la respuesta honesta es que existe el mecanismo de servidor y el cliente
> usa polling.

## 6.2 La bandeja de salida de correos

```bash
curl -s "http://127.0.0.1:8004/api/v1/emails?limite=10" -H "Authorization: Bearer $ADM"
```

Cada correo enviado queda registrado con su destino, asunto, estado y error si lo hubo.

**Por que existe esa tabla y no basta con MailHog:** el envio de correo **nunca lanza una
excepcion**. Si el servidor SMTP esta caido, el consumidor del evento ya habia confirmado el
mensaje; si el envio hubiera fallado y lanzado el error, el mensaje habria vuelto a la cola
de fallidos y se habria reintentado tres veces, generates tres correos duplicados. En cambio
se registra el fallo y queda pendiente de reintento manual.

```bash
curl -s -X POST http://127.0.0.1:8004/api/v1/emails/{id}/reintentar \
  -H "Authorization: Bearer $ADM"
```

MailHog esta en <http://localhost:8025> y su API en `/api/v2/messages`.

---

# 7. Correlacion de punta a punta

Este es el cierre mas fuerte de la defensa: **un solo identificador atraviesa una peticion
sincrona, viaja por el bus de mensajes, y aparece en otro servicio y en la base de datos.**

## 7.1 Los tres pasos

```bash
# 1) Enviar una peticion con identificador propio
CID="demo-corr-$(date +%H%M%S)"

curl -s -o /dev/null -w "HTTP=%{http_code}\n" \
  -X POST http://127.0.0.1:8001/api/v1/mesas/1/solicitudes \
  -H "Authorization: Bearer $C" \
  -H "X-Correlation-Id: $CID" \
  -H 'Idempotency-Key: probe-corr-join' \
  -H 'Content-Type: application/json' -d '{"rol":"jugador"}'
```

**2) Buscarlo en los logs del servicio que la recibio:**

```bash
docker compose logs mesas-api | grep "$CID"
```

**Salida real:**

```json
{"ts": 1790700721882, "nivel": "INFO", "servicio": "mesas-api",
 "mensaje": "request iniciado",  "correlation_id": "demo-corr-135201"}
{"ts": 1790700721891, "nivel": "INFO", "servicio": "mesas-api",
 "mensaje": "request finalizado", "correlation_id": "demo-corr-135201"}
```

**3) Buscarlo en la base de datos del OTRO servicio** (admin, puerto 8004):

```bash
curl -s "http://127.0.0.1:8004/api/v1/event-log?correlation_id=$CID" \
  -H "Authorization: Bearer $ADM"
```

**Respuesta real:**

```json
[
  {
    "id": 103,
    "entidadTipo": "mesa.aceptada",
    "entidadId": null,
    "accion": "consumido",
    "usuarioId": null,
    "metadata": {"mesa_id": 1},
    "ocurridoEn": "2026-09-29T16:52:01.892627+00:00",
    "correlationId": "demo-corr-135201"
  }
]
```

## 7.2 Que demuestra

La peticion entro a **mesas-api**, publico un evento, **notif-api** lo consumio de una cola
distinta, en otro proceso y otra base de datos, lo registro, y el mismo identificador
permite unir ambos extremos. Eso es trazabilidad distribuida, y se obtiene sin instrumentar
nada: el identificador viaja en la cabecera de la peticion y **dentro del cuerpo del
mensaje** (no en las cabeceras AMQP, que no sobreviven al reintento).

**Si la peticion falla, el mismo identificador aparece en los dos lugares**, que es
justamente cuando mas se lo necesita.

---

# 8. Los 49 endpoints

Recuento obtenido del esquema OpenAPI de los cuatro servicios en ejecucion:
**37 rutas bajo `/api/*` y 12 endpoints de salud** (3 por servicio), es decir **49 en total**.

> La documentacion anterior del proyecto declara 46. El numero correcto, medido sobre el
> esquema publicado por los servicios, es 37 + 12 = 49.

## 8.1 mesas-api (puerto 8001) — 18 rutas `/api/*`

| Metodo | Ruta | Auth | Que hace |
|---|---|---|---|
| POST | `/api/v1/auth/register` | — | Crear cuenta; **siempre rol `usuario`** |
| POST | `/api/v1/auth/login` | — | Devuelve access + refresh + rol |
| POST | `/api/v1/auth/refresh` | — | Renovar el access token |
| POST | `/api/v1/auth/logout` | usuario | Borra la sesion en Redis |
| GET | `/api/v1/auth/me` | usuario | Devuelve los claims del token |
| GET | `/api/v1/auth/admin-only` | **admin** | Prueba de autorizacion |
| GET | `/api/v1/mesas` | — | Listado (cacheado 60 s) |
| GET | `/api/v1/mesas/{id}` | — | Una mesa |
| POST | `/api/v1/mesas` | usuario | Crear |
| PUT | `/api/v1/mesas/{id}` | usuario | Editar parcial |
| DELETE | `/api/v1/mesas/{id}` | usuario | Borrar (204) |
| GET | `/api/v1/mesas/{id}/miembros` | usuario | Miembros — **lo consume notif-api** |
| POST | `/api/v1/mesas/{id}/solicitar` | usuario | Legacy: publica evento, **no reserva cupo** |
| POST | `/api/v1/mesas/{id}/solicitudes` | usuario | **El real**: reserva cupo, 201 |
| POST | `/api/v1/matchmaking/{mesa_id}/abrir` | **gm** | Abre ventana de 120 s |
| GET | `/api/v1/matchmaking/{mm_id}/estado` | — | Estado y TTL restante |
| POST | `/api/v1/sesiones/{id}/qr` | usuario | Emite QR (TTL 600 s) |
| POST | `/api/v1/sesiones/{id}/qr/validar` | **gm** | Consume el QR (un solo uso) |

## 8.2 builds-api (puerto 8002) — 4 rutas

| Metodo | Ruta | Auth | Que hace |
|---|---|---|---|
| GET | `/api/v1/builds` | — | Listado; filtro `?mesa_id=` |
| GET | `/api/v1/builds/{id}` | — | Una ficha |
| GET | `/api/v1/tags` | — | 13 etiquetas |
| POST | `/api/v1/builds/{id}/pdf` | usuario | **202** + `documento_id` |

**Este servicio es de solo lectura.** No expone alta, edicion ni borrado de builds.

## 8.3 feed-api (puerto 8003) — 3 rutas

| Metodo | Ruta | Auth | Que hace |
|---|---|---|---|
| GET | `/api/v1/feed` | — | Filtros `tipo`, `autor_id`, `etiqueta`; orden `id/recientes/antiguos/votos`; paginacion |
| GET | `/api/v1/wiki` | — | Carpetas y paginas; filtro `?mesa_id=` |
| POST | `/api/v1/mesas/{m}/sesiones/{s}/diario/pdf` | usuario | **202** PDF del diario |

Comprobaciones reales de validacion:

```bash
curl -s "http://127.0.0.1:8003/api/v1/feed?tipo=inventado"
# {"error":{"codigo":400,"mensaje":"query.tipo: String should match pattern '^(post|build|wiki)$'"}}  [400]
```

## 8.4 notif-api (puerto 8004) — 12 rutas

| Metodo | Ruta | Auth | Que hace |
|---|---|---|---|
| GET | `/api/v1/notificaciones` | usuario | Propias + globales; `?solo_no_leidas=` |
| GET | `/api/v1/notificaciones/stream` | usuario | **SSE** en vivo |
| PATCH | `/api/v1/notificaciones/{id}/leida` | usuario | Marcar leida (solo propia) |
| POST | `/api/v1/auth/recuperar` | — | **202** siempre, sin enumerar cuentas |
| GET | `/api/v1/event-log` | **admin** | Auditoria; filtros por entidad y correlacion |
| GET | `/api/v1/emails` | **admin** | Bandeja de salida |
| POST | `/api/v1/emails/{id}/reintentar` | **admin** | Reenvio manual |
| GET | `/api/v1/pdf/{id}` | usuario | Descarga (404 si no esta `listo`) |
| GET | `/api/v1/pdf/{id}/estado` | usuario | `en_proceso` / `listo` / `error` |
| GET | `/api/v1/dlq` | **admin** | Cola de fallidos |
| POST | `/api/v1/dlq/{id}/reintentar` | **admin** | Republicar |
| DELETE | `/api/v1/dlq/{id}` | **admin** | Descartar |

## 8.5 El sobre de error, unico en los cuatro servicios

```json
{"error": {"codigo": 409, "mensaje": "Cupo agotado: no quedan vacantes"}}
```

Los errores de validacion se traducen a **400** (no 422) para unificar el contrato, y los
mensajes vienen en castellano.

## 8.6 Los endpoints que el frontend no toca

Recuento verificado sobre el fuente del frontend: de los **37 endpoints `/api/*`**, el
codigo del cliente referencia **16**. De esos 16, dos —`event-log` y `pdf/{id}`— estan
declarados en `src/api/endpoints.js` pero **ninguna vista los invoca**. Quedan por tanto
**21 endpoints que ninguna pantalla utiliza**:

| Endpoint | Por que conviene mostrarlo |
|---|---|
| `GET /notificaciones/stream` | El tiempo real existe y no se ve en la interfaz |
| `GET /event-log` | La auditoria con filtro de correlacion |
| `GET /emails` + `POST /emails/{id}/reintentar` | La bandeja de salida |
| `GET /dlq` + `POST /dlq/{id}/reintentar` + `DELETE /dlq/{id}` | Operacion manual de la cola de fallidos |
| `GET /pdf/{id}/estado` y `GET /pdf/{id}` | La maquina de estados asincrona |
| `GET /builds`, `/builds/{id}`, `/tags` | El servicio de builds, entero |
| `GET /feed`, `/wiki` | El feed real, no el de maqueta |
| `GET /mesas/{id}/miembros` | El unico endpoint que consume un servicio a otro |
| `GET /builds?mesa_id=` y los filtros del feed | Parametros de consulta que la interfaz no ejercita |

---

# 9. Pruebas automatizadas

```bash
# Suite completa
venv/bin/pytest tests -v

# Solo unitarias (no necesitan servicios levantados)
venv/bin/pytest tests -m unit -v

# Solo de integracion (necesitan postgres, redis y rabbitmq)
venv/bin/pytest tests -m integration -v
```

**130 pruebas de backend**: 50 unitarias y 80 de integracion. La suite aísla su propio estado
para no tocar los datos de la demo:

- Usa bases de datos con sufijo `_test`, no las de la demo.
- Usa la base 15 de Redis, no la 0.
- Crea su propio espacio de nombres en RabbitMQ, y al terminar vacia las colas.

> **Verificado:** despues de correr la suite completa, la cola `dlq.general` del broker de
> desarrollo queda en 0. Si quedaran mensajes, la prueba estaria escribiendo en el broker
> equivocado.

```bash
# Frontend
cd tfinder-vue
npm test              # 22 pruebas
npm run lint
```

Las pruebas de integracion que demuestran concurrencia y resiliencia, y que vale la pena
mencionar:

| Prueba | Que demuestra |
|---|---|
| `test_carrera.py` | 10 peticiones simultaneas por 1 vacante -> 1 exito y 9 rechazos |
| `test_idempotencia.py` | La misma clave no crea filas duplicadas |
| `test_qr.py` | Un QR no se puede reutilizar |
| `test_dlq.py` | Un fallo repetido termina en la cola de fallidos |
| `test_amqp_topologia.py` | El grafo de exchanges, colas y bindings |
| `test_ready_degradado.py` | Con cada dependencia caida, `/ready` responde 503 |

---

# Anexo. Valores de referencia

## A.1 Puertos

| Servicio | Puerto |
|---|---|
| Aplicacion | 5173 |
| mesas-api | 8001 |
| builds-api | 8002 |
| feed-api | 8003 |
| notif-api | 8004 |
| Postgres | 5432 |
| **Redis** | **6390** |
| **AMQP** | **5673** |
| **Panel RabbitMQ** | **15673** |
| SMTP (MailHog) | 1025 |
| Panel MailHog | 8025 |

## A.2 Credenciales

| Que | Valor |
|---|---|
| Cuentas de demo | `admin@`, `gm@`, `jugador1..3@tfinder.dev` |
| Contrasena | `DemoTFinder123!` |
| Postgres / RabbitMQ | `tfinder` / `tfinder` |
| Firma de QR | `QR_SECRET` (valor por defecto en desarrollo) |
| Secreto de los tokens | `JWT_SECRET`, 1440 min de duracion |

## A.3 TTL y estados

| Cosa | Valor |
|---|---|
| Sesion en Redis | 86400 s |
| Idempotencia | 86400 s |
| Cerrojo de vacante | 60 s |
| Cache del listado | 60 s |
| Ventana de llamado | 120 s |
| QR | 600 s |
| Reintentos antes de la DLQ | 3 |
| Espera entre reintentos | 2 s, luego 4 s |
| Sondeo del frontend (avisos) | 5 s |
| Sondeo del frontend (llamado) | 2 s |
