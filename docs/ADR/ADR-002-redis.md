# ADR-002 · Redis para sesiones, caché, reservas y QR (TTL vs invalidación)

- Estado: **Aceptado**
- Fecha: 2026-09-23

## Contexto

Se necesitaba un almacenamiento de valores con expiración automática y semántica atómica por clave, para cuatro usos distintos: sesiones JWT revisables (B03), caché del listado de mesas (B02), reserva de la carrera por vacante (B06) y QR de asistencia single-use (B07). PostgreSQL no ofrece TTL a nivel fila de forma natural ni `SET NX`/`GETDEL` tan directos.

## Decisión

Usar **Redis 7** (publicado por compose; host `6390`, interno `6379`) como store auxiliar por dominio:

- **Sesiones**: `SETEX sesion:{jti} 86400` → revocación por logout/expiración (B03).
- **Caché**: `SETEX cache:mesas:list 60` con **invalidación explícita** (`DELETE`) en writes (crear/actualizar/eliminar mesa), tolerando TTL corto como red de seguridad (B02).
- **Reservas**: `SET reserva:vacante:{mesa} NX EX 60` → serializa la entrada a la sección crítica (B06).
- **QR**: `SETEX qr:{sesion}:{usuario} 600` + `GETDEL` en la validación → single-use exacto (B07).
- Redis también guarda las claves de idempotencia (`idem:solicitud:{key}`) y la sesión del acceso de notif-api a mesas-api (token cacheador, B09).

## Consecuencias

- **Positivas**: expiración automática que evita limpiezas manuales; operaciones atómicas (NX/GETDEL) que el resto del stack no ofrece; db 15 aislada para tests.
- **Negativas**: Redis introduce una dependencia más en `/ready`; si cae, quedan sin servicio sesiones, caché, reservas y QR (los logs y la API lo degradan vía 503); la invalidación de caché es por evento de escritura y hay que recordarla en cada write (riesgo de cache obsoleto si se agrega un write sin `invalidar_listado`).