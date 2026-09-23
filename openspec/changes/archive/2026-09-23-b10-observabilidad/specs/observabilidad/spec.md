## Purpose

Define la observabilidad base de TFinder AE2 (RNF-13, RNF-16): logs estructurados en JSON con `correlation_id` en los 4 servicios, propagación del identificador de correlación por header y hacia mensajes de eventos, y endpoints `/live`/`/ready` para verificar el proceso y sus dependencias, sin emitir datos sensibles en los logs.

## ADDED Requirements

### Requirement: Logs JSON estructurados con correlación
Los 4 servicios DEBEN emitir sus logs en una única línea JSON por registro con los campos `ts`, `nivel`, `servicio`, `mensaje` y `correlation_id` (default `-`), y `exc` opcional con el traceback cuando exista excepción, mediante un módulo compartido `app/infra/logge.py`.

#### Scenario: Salida JSON por servicio
- **WHEN** se emite cualquier log de nivel INFO o superior en cualquiera de los 4 servicios
- **THEN** la línea de consola es un objeto JSON con `ts`, `nivel`, `servicio`, `mensaje` y `correlation_id` presentes

#### Scenario: Traceback estructurado
- **WHEN** el logger registra una excepción con `exc_info`
- **THEN** el JSON incluye el campo `exc` con el traceback formateado

### Requirement: Correlation id por header X-Correlation-Id
Cada servicio DEBE aceptar `X-Correlation-Id` en el request HTTP y usarlo como `correlation_id` en los logs del recorrido; si no viene, DEBEn generar uno nuevo. El middleware DEBE registrar la entrada y salida del request con el mismo CID y reflejarlo en el header de respuesta.

#### Scenario: CID provisto por el cliente
- **WHEN** un request llega con `X-Correlation-Id: cid-test-42`
- **THEN** los logs de entrada y salida de ese request en el servicio usan `correlation_id: cid-test-42` y la respuesta incluye `X-Correlation-Id: cid-test-42`

#### Scenario: CID autogenerado
- **WHEN** un request llega sin `X-Correlation-Id`
- **THEN** el servicio genera un CID (16 chars hex) y todos los logs de ese recorrido comparten ese valor

### Requirement: Propagación del correlation id a mensajes publicados
El módulo compartido DEBE inyectar `correlation_id` en el payload de los mensajes RabbitMQ publicados (tomando el del contexto del request), de modo que `request → evento → consumer` rastree el mismo CID.

#### Scenario: Mensaje con correlación
- **WHEN** se publica un mensaje durante un request con CID conocido
- **THEN** el payload del mensaje lleva el campo `correlation_id` con ese valor, y un consumidor que lo registre en `event-log` permite grepear el CID punta a punta

### Requirement: Endpoints de salud /live y /ready
Los 4 servicios DEBEN exponer `GET /live` (responde `200` si el proceso responde, sin dependencias) y `GET /ready` (responde `200` con `{"estado":"listo","dependencias":{...}}` solo si PostgreSQL, Redis y RabbitMQ responden, o `503` con `{"estado":"degradado",...}` si alguna falla).

#### Scenario: Ready completo
- **WHEN** PostgreSQL, Redis y RabbitMQ responden y se consulta `/ready`
- **THEN** la respuesta es `200` con `estado: listo` y las tres dependencias en `true`

#### Scenario: Ready degradado
- **WHEN** alguna dependencia (p. ej. PostgreSQL) no responde y se consulta `/ready`
- **THEN** la respuesta es `503` con `estado: degradado` y las dependencias fallidas en `false`

#### Scenario: Live sin dependencias
- **WHEN** se consulta `/live` aun con dependencias caídas
- **THEN** la respuesta es `200` con `estado: vivo`

### Requirement: Logs sin datos sensibles
Los servicios DEBEN abstenerse de registrar tokens JWT, contraseñas y QRs completos en los logs; los identificadores/valores sensibles se enmascaran o se omite.

#### Scenario: Ausencia de secretos en logs
- **WHEN** se revisan las líneas JSON emitidas por un recorrido autenticado
- **THEN** no aparece ningún token de acceso/refresh, contraseña ni QR completo en ningún campo