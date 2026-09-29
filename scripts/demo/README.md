# Demos de la presentación de 15 minutos

Todos los comandos de la presentación, agrupados por sección y verificados contra el stack
en vivo. Cada script imprime lo que se está mirando, el resultado esperado y, al final,
si hubo alguna diferencia con lo verificado.

## Uso

```bash
bash scripts/demo/00-reset.sh          # UNA vez, antes de empezar
bash scripts/demo/01-preparacion.sh
bash scripts/demo/02-mesas.sh
...
bash scripts/demo/12-qr.sh             # opcional, si sobra tiempo
```

Si algo falla, primero:

```bash
bash scripts/demo/99-diagnostico.sh
```

## Los scripts

| # | Archivo | Qué demuestra | Tiempo |
|---|---|---|---|
| 00 | `00-reset.sh` | Stack arriba con datos limpios. **Borra todo**, es el único que lo hace | ~3 min |
| 01 | `01-preparacion.sh` | Los 4 servicios, el frontend y los 4 tokens | ~5 s |
| 02 | `02-mesas.sh` | Estado de las mesas, topología y checklist previo | ~5 s |
| 03 | `03-arquitectura.sh` | Slides 8, 13 y 14. Acepta `bases`, `rutas`, `errors` o `todas` | ~3 s |
| 04 | `04-concurrencia.sh` | Slide 9: la carrera por la última vacante y **las dos barreras** | ~3 s |
| 05 | `05-redis.sh` | Slide 10: TTL de 60 s e invalidación explícita del caché | ~3 s |
| 06 | `06-asincronia.sh` | Slide 11: topología de RabbitMQ y el PDF asíncrono de punta a punta | ~5 s |
| 07 | `07-seguridad.sh` | Slide 12: modo degradado y correlación de punta a punta | ~8 s |
| 08 | `08-idempotencia.sh` | Slide 15: el replay devuelve la misma fila y no consume otra vacante | ~3 s |
| 09 | `09-recorrido.sh` | Slide 16: el recorrido de la aplicación en 8 pasos, con SSE | ~15 s |
| 10 | `10-gating.sh` | Slide 17: 20 features y la matriz de acceso entera | ~5 s |
| 11 | `11-testing.sh` | Slide 18: 22 de frontend y 130 de backend | ~20 s |
| 12 | `12-qr.sh` | Demo extra: el QR de un solo uso, `200` y después `409` | ~2 s |
| 99 | `99-diagnostico.sh` | Por qué falló: token, sesión en Redis, secretos, cuentas, logs | ~5 s |

`03-arquitectura.sh` cubre tres slides separadas en el tiempo, así que acepta qué parte correr:

```bash
bash scripts/demo/03-arquitectura.sh bases     # slide 8
bash scripts/demo/03-arquitectura.sh rutas     # slide 13
bash scripts/demo/03-arquitectura.sh errores   # slide 14
bash scripts/demo/03-arquitectura.sh           # las tres
```

`_lib.sh` es la compartida. No se ejecuta sola.

## Cómo se leen

```
-- algo                la sección
  esperado: ...        lo que tiene que salir, para comparar mientras se habla
  OK                   coincidió con lo verificado
  FALLO                no coincidió; al final se cuenta y se dice qué hacer
```

## Qué NO es re-ejecutable

`04-concurrencia.sh` **necesita la mesa 2 en 3/4** y la deja en 4/4. `02-mesas.sh` avisa si el
estado no es el de demostración. Si ya corriste la demo y querés volver a empezar:

```bash
bash scripts/demo/00-reset.sh && bash scripts/demo/01-preparacion.sh
```

Los demás sí se pueden correr las veces que quieras: `08` y el paso 5 de `09` crean su propia
mesa de prueba.

## Detalles que hacen que no se rompa en vivo
- `07-seguridad.sh` tiene un `trap` en `EXIT` que **despausa Redis** aunque lo interrumpas con
  Ctrl-C. Sin eso, todo lo que sigue devuelve `401`.
- Las llamadas que se usan para *verificar* un código no tienen efecto: el código y el cuerpo
  salen de la misma petición. Antes, una segunda llamada de verificación movía el contador de la
  mesa.
- Ninguna demostración depende de la anterior salvo la 9, que avisa.
- Todos los scripts funcionan desde cualquier directorio.
