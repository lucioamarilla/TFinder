## Purpose

Provee el entorno de desarrollo reproducible de TFinder: servicios de infraestructura (PostgreSQL, Redis, RabbitMQ, MailHog) levantados con Docker Compose, configuración 100 % por variables de entorno sin secretos en el código, y clientes compartidos de Redis y RabbitMQ para el resto de los servicios AE2.

## ADDED Requirements

### Requirement: Entorno reproducible con un comando
El sistema SHALL exponer una definición Docker Compose que permita levantar los servicios PostgreSQL, Redis, RabbitMQ y MailHog con un único comando, y cada servicio DEBE quedar con estado `healthy` (o `running` para MailHog) sin errores cuando se consulta `docker compose ps`.

#### Scenario: Levantamiento de los cuatro servicios de infraestructura
- **WHEN** se ejecuta `docker compose up -d postgres redis rabbitmq mailhog`
- **THEN** los cuatro contenedores quedan corriendo y los tres con healthcheck declarado reportan `healthy` en `docker compose ps` sin errores

#### Scenario: Estado verificable tras el arranque
- **WHEN** se ejecuta `docker compose ps`
- **THEN** la salida muestra los servicios `tfinder-postgres`, `tfinder-redis`, `tfinder-rabbitmq` y `tfinder-mailhog` en estado `running` y sin errores

### Requirement: Base de datos por servicio
El sistema SHALL exponer una instancia PostgreSQL con cuatro bases de datos listas para los servicios: `mesas_db`, `builds_db`, `feed_db` y `notif_db`.

#### Scenario: Las cuatro bases existen al primer arranque
- **WHEN** postgres se levanta por primera vez con el volumen vacío (o se resetea el volumen)
- **THEN** las bases `mesas_db`, `builds_db`, `feed_db` y `notif_db` existen y son listadas por una consulta de catálogo (`psql -l` o equivalente)

#### Scenario: Conexión verificable por el driver
- **WHEN** un cliente `psycopg` se conecta a `postgresql://tfinder:tfinder@localhost:5432/mesas_db` y ejecuta `select 1`
- **THEN** la consulta devuelve `(1,)` y la conexión no arroja errores

### Requirement: Configuración por variables de entorno sin secretos
El sistema SHALL configurarse por variables de entorno documentadas en `.env.example` sin valores sensibles, de modo que no existan secretos ni credenciales hardcodeadas en el código ni en los archivos versionados.

#### Scenario: Documentación completa de variables
- **WHEN** se revisa `.env.example`
- **THEN** documenta al menos `PORT`, `DATABASE_URL`, `REDIS_URL`, `RABBITMQ_URL`, `SMTP_HOST`, `SMTP_PORT`, `MAIL_FROM`, `JWT_SECRET` y `JWT_EXP_MIN`, y ninguno de sus valores es un secreto real (el contenido es de ejemplo/demostración)

#### Scenario: Clientes que leen el entorno
- **WHEN** un módulo interno necesita Redis o RabbitMQ
- **THEN** usa valores provenientes de `REDIS_URL` y `RABBITMQ_URL` del ambiente, con un default de desarrollo local para el entorno de compose, sin credenciales en el código fuente

### Requirement: Clientes compartidos de infraestructura
El sistema SHALL proveer acceso centralizado a Redis y RabbitMQ mediante un módulo de infraestructura que los demás módulos puedan reutilizar.

#### Scenario: Obtención del cliente Redis
- **WHEN** se pide el cliente Redis del módulo compartido
- **THEN** devuelve un cliente configurado según `REDIS_URL` (o su default local) y responde `True` a `ping()` cuando el servicio está activo

#### Scenario: Obtención de parámetros de conexión RabbitMQ
- **WHEN** se piden los parámetros de conexión a RabbitMQ del módulo compartido
- **THEN** devuelve `ConnectionParameters` derivados de `RABBITMQ_URL` (o su default local) utilizables por un cliente `pika`

### Requirement: API integrado al entorno de contenedores
El sistema SHALL permitir que el API existente corra dentro de un contenedor de la misma red de compose, o bien apunte a dicha red desde el host, DE forma que su configuración de entorno sea consistente con los servicios de infraestructura.

#### Scenario: API corriendo desde imagen propia
- **WHEN** se construye y levanta el servicio `api` con `docker compose build api && docker compose up -d api`
- **THEN** el contenedor expone el API en el puerto configurado por `PORT` y responde en `/docs` sin errores

### Requirement: Verificación rigurosa automatizable
El sistema SHALL soportar un conjunto de verificaciones definitivas (definición de done) que fallen con código de salida distinto de cero si algún servicio de infraestructura no responde.

#### Scenario: Verificación de PostgreSQL
- **WHEN** se ejecuta la verificación de `psycopg` contra `mesas_db` con la aserción del resultado esperado
- **THEN** el comando sale con código `0` si el valor consultado es `(1,)`, y con código distinto de cero en cualquier otro caso

#### Scenario: Verificación de Redis
- **WHEN** se ejecuta la verificación de `redis` con aserción sobre `ping()`
- **THEN** el comando sale con código `0` si el servicio responde `PONG`, y con código distinto de cero en cualquier otro caso

#### Scenario: Acceso a paneles de soporte
- **WHEN** se abre el panel de RabbitMQ en el puerto de management publicado y el de MailHog en su puerto web
- **THEN** ambos cargan su interfaz con las credenciales/URLs de desarrollo provistas