# Manual de usuario de TFinder

## 1. Qué es TFinder

TFinder es una aplicación para encontrar y seguir campañas de juegos de mesa. En la versión actual permite explorar mesas, consultar sus detalles, registrarse, iniciar sesión y solicitar unirse a una mesa abierta.

Las funciones activas adicionales son crear y editar mesas, asistencia por QR, matchmaking, recuperación de contraseña y notificaciones. El resto de las funciones avanzadas se encuentra en preparación y muestra **Próximamente** cuando se abre desde la navegación o una URL directa.

## 2. Acceder a la aplicación

1. Abrir `http://localhost:5173` si la aplicación está ejecutada localmente.
2. Esperar a que la página de inicio aparezca.
3. Pulsar **Explorar Mesas** para ver las campañas disponibles.

Si la página no abre, verificar que el frontend esté iniciado y que el navegador no tenga un proxy bloqueando `localhost`.

## 3. Crear una cuenta

1. Pulsar **Registrarse**.
2. Completar:
   - Nombre.
   - Email válido.
   - Contraseña de al menos 8 caracteres.
3. Revisar los datos.
4. Pulsar el botón de registro.
5. Si la cuenta se crea correctamente, iniciar sesión con el email y la contraseña elegidos.

La aplicación no debe usarse con contraseñas reales en instalaciones de demostración.

## 4. Iniciar sesión

1. Pulsar **Iniciar sesión**.
2. Escribir el email y la contraseña.
3. Pulsar **Iniciar sesión**.
4. Confirmar que la sesión queda activa.

Si el acceso falla, revisar mayúsculas, espacios y correo. El mensaje de error no debe usarse para determinar si un email está registrado.

### Cuentas de demostración

Todos los usuarios demo usan la contraseña:

```text
DemoTFinder123!
```

| Email | Uso recomendado |
|---|---|
| `admin@tfinder.dev` | Administrador |
| `gm@tfinder.dev` | Game Master |
| `jugador1@tfinder.dev` | Jugador |
| `jugador2@tfinder.dev` | Jugador |
| `jugador3@tfinder.dev` | Jugador |

Estas cuentas existen solamente cuando la instalación tiene los datos demo habilitados.

## 5. Explorar mesas

Desde **Explorar Mesas** se puede:

- Ver todas las mesas disponibles.
- Buscar por nombre.
- Filtrar por sistema de juego.
- Filtrar por disponibilidad.
- Ordenar resultados.
- Limpiar los filtros aplicados.
- Actualizar el listado.

Los filtros del listado se aplican en el navegador. Si una búsqueda no devuelve resultados, comprobar que el texto no sea demasiado restrictivo y pulsar **Limpiar filtros**.

## 6. Ver el detalle de una mesa

1. Pulsar una mesa del listado.
2. Revisar su nombre.
3. Comprobar sistema de juego.
4. Leer la descripción o lore.
5. Revisar estado, ocupación y número máximo de jugadores.

Una mesa puede estar abierta, casi llena o cerrada. La cantidad `2/4` significa que hay 2 jugadores ocupados de un máximo de 4.

Si el detalle no existe o no se puede cargar, volver al listado y abrir otra mesa.

## 7. Solicitar unirse

1. Iniciar sesión.
2. Abrir una mesa abierta con plazas disponibles.
3. Pulsar la acción para unirse o solicitar unión.
4. Esperar la confirmación.

Resultados posibles:

- **Solicitud enviada:** la operación fue aceptada.
- **Cupo agotado:** la mesa ya no tiene vacantes.
- **Ya solicitaste o registraste la solicitud:** revisar el estado de la mesa.
- **No se pudo conectar:** la mesa no responde; reintentar más tarde.

La aplicación utiliza una clave de idempotencia para evitar que un doble clic cree dos solicitudes para la misma mesa y usuario.

## 8. Sesión y cierre de sesión

La sesión iniciada se conserva al recargar la página. Para terminar la sesión:

1. Abrir el menú de usuario.
2. Pulsar **Cerrar sesión**.
3. Confirmar que la sesión terminó y que el acceso a páginas protegidas ya no está disponible.

Si se cierra el navegador, la sesión puede continuar vigente según la configuración del entorno. Cerrar sesión explícitamente es la opción más segura en equipos compartidos.

## 9. Crear y editar mesas

Requiere sesión iniciada.

1. Abrir el formulario de nueva mesa.
2. Completar nombre, sistema, descripción, horario y capacidad.
3. Guardar la mesa y verificar que aparezca en el listado.
4. Para editar, abrir la mesa y usar la opción de edición.

## 10. Notificaciones

1. Con la sesión iniciada, pulsar la campana del encabezado.
2. Revisar el listado de avisos y los filtros por grupo.
3. Abrir un aviso sin leer para marcarlo como leído.
4. Usar la opción de marcar todas como leídas si corresponde.

El contador de avisos sin leer se actualiza solo cada 5 segundos y también al marcar lecturas. Si el servicio de notificaciones no responde, la campana se atenúa y el contador queda en cero hasta que vuelva la conexión.

Cada usuario solo ve sus propios avisos y los avisos generales de la comunidad. Marcar como leído un aviso ajeno no es posible.

## 11. Asistencia por QR

1. Iniciar sesión como Game Master de la mesa.
2. Abrir la sesión y generar el código QR de asistencia.
3. Validar el código desde la vista de sesión.

## 12. Matchmaking

1. Abrir la vista de matchmaking con la sesión iniciada.
2. Elegir una mesa y abrir su cola de matchmaking.
3. Consultar el estado de la cola.

## 13. Recuperación de contraseña

1. Ir a la pantalla de inicio de sesión.
2. Usar el enlace de recuperación de contraseña.
3. Escribir el email de la cuenta.
4. Confirmar que la solicitud fue aceptada.

La respuesta no debe revelar si el email existe en el sistema.

## 14. Encuentros

1. Iniciar sesión y abrir **Encuentros** desde la navegación.
2. Elegir nivel de grupo, dificultad y entorno.
3. Pulsar el botón de tirar el encuentro.
4. Revisar la composición del grupo, el CR sugerido y el botín.

Es una herramienta de preparación de sesión: el resultado se calcula en el navegador y no se guarda en ningún servidor. Para conservarlo, anotarlo a mano o copiarlo al diario de la sesión.

## 15. Funciones en preparación

Actualmente muestran **Próximamente** las siguientes áreas:

- Dashboard.
- Perfil extendido.
- Mis campañas.
- Gestión de campaña.
- Wiki.
- Calendario y votación.
- Sesiones y diario.
- Gestión de jugadores.
- Builds.
- Feed Social.
- Directorio de aventureros.
- Administración.

Al abrir cualquiera de ellas se debe ver el nombre de la función, el estado **Próximamente** y un enlace para volver a explorar mesas. No asumir que estas áreas permiten realizar operaciones todavía.

## 16. Problemas frecuentes

### La página no carga

1. Verificar la URL `http://localhost:5173`.
2. Comprobar que el contenedor del frontend esté activo.
3. Recargar con Ctrl+R o Cmd+R.
4. Si persiste, abrir la terminal y consultar los logs.

### No aparecen mesas

- Verificar que la API de mesas esté activa.
- Revisar `/ready` en `http://localhost:8001/ready`.
- Pulsar **Limpiar filtros**.
- Recargar el listado.
- Comprobar que el caché de mesas no esté mostrando datos antiguos; puede tardar hasta 60 segundos en invalidarse.

### El login no funciona

- Revisar email y contraseña.
- Confirmar que la cuenta tiene al menos 8 caracteres de contraseña.
- Verificar que la API de mesas esté disponible.
- Si la sesión quedó corrupta, cerrar sesión o limpiar los datos del sitio y volver a iniciar sesión.

### El botón de unión falla

- Comprobar que la mesa esté abierta y tenga vacantes.
- Verificar que la sesión siga activa.
- Esperar unos segundos y reintentar.
- Si el problema continúa, usar otra mesa de demostración.

### La sesión termina sola

Puede ocurrir si el token expiró, se cerró la sesión, se restauró Redis o el backend se reinició con una configuración de secretos diferente. Iniciar sesión nuevamente.

## 17. Privacidad y seguridad

- Usar una contraseña diferente para cualquier instalación real.
- No compartir tokens, contraseñas o capturas con información sensible.
- Cerrar sesión al terminar.
- No utilizar datos personales reales en el ambiente de demostración.
- Las restricciones visuales del frontend no sustituyen los permisos del backend.
- Ante un comportamiento inesperado, conservar la evidencia y reportar la URL, la acción y el mensaje exacto.

## 18. Resumen del flujo actual

```text
Inicio
  → Explorar mesas
  → Abrir mesa
  → Iniciar sesión
  → Solicitar unirse
  → Esperar confirmación
  → Revisar notificaciones
```

Además de este flujo, las funciones activas incluyen crear y editar mesas, asistencia por QR, matchmaking, recuperación de contraseña y el generador de encuentros. El resto de las áreas está preparado para futuras versiones y debe comunicarse como **Próximamente**, no como una función operativa.
