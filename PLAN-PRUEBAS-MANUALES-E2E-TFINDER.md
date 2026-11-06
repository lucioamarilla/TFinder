# Plan de Pruebas Manuales E2E · Tfinder

> Aplicación web Tfinder (mesas de Pathfinder 1e, gestión de campaña, builds PF1e, feed, notificaciones, consola admin).  
> Documento generado para ejecución manual por un QA Lead; cada caso incluye pasos, resultado esperado (UI + backend) y estado.  
> **Simbología de estado:** `[ ]` Pendiente · `[x]` Pasó · `[!]` Falló · `[-]` Bloqueado por otro defecto.  
> **Precondiciones generales:** entorno levantado (`docker compose up -d` o `dev.py up`); backend en `:8001-8004`; frontend en `:5173`; Postgres/Redis/RabbitMQ sanos; navegador con devtools abierto (consola + network).  
> **Datos de prueba:** cuentas `gm@tfinder.dev / DemoTFinder123!` (GM), `navuno@tfinder.dev` (jugador), `admin@tfinder.dev` (admin — crear con `scripts/bootstrap_admin.py`), mesas demo 1-4, mesa creada por el usuario para pruebas de gestión, al menos 1 build publicado.

---

## 1. Información general y preparación

### 1.1 Precondiciones del entorno
- [ ] `docker compose up -d` (o `dev.sh`/`dev.py`) deja los 7 servicios `healthy` (postgres, redis, rabbitmq, mailhog, mesas-api, builds-api, feed-api, notif-api, frontend).
- [ ] Frontend accesible en `http://localhost:5173` con el tema correcto (arcade oscuro, sin pergamino global).
- [ ] Variables de entorno `VITE_AUTH_MODE=api` y `VITE_API_MODE=api` en el build del frontend.
- [ ] Cuentas de prueba creadas o registradas; al menos un GM con mesa propia y un jugador miembro de otra mesa.
- [ ] `localStorage` limpio antes de cada bloque (logout + borrar storage) para aislar sesiones.
- [ ] DevTools: pestaña Network filtrando por `api` y Console con errores habilitados.

### 1.2 Simbología de estados
- `[ ]` Pendiente · `[x]` Pasó · `[!]` Falló · `[-]` Bloqueado por otro defecto.

### 1.3 Convenciones de IDs
- `TC-AUTH-xxx` Autenticación · `TC-NAV-xxx` Navegación/Layout · `TC-MESA-xxx` Catálogo/Detalle · `TC-CREAR-xxx` Crear/Editar mesa · `TC-GM-xxx` Panel GM · `TC-GES-xxx` Gestión de campaña · `TC-CAL-xxx` Calendario/Votación · `TC-SES-xxx` Sesiones/Diario/QR · `TC-WIKI-xxx` Wiki · `TC-JUG-xxx` Jugadores/Solicitudes · `TC-BUILD-xxx` Builds · `TC-FEED-xxx` Feed · `TC-ENC-xxx` Encuentros · `TC-TAG-xxx` Tags · `TC-NOTIF-xxx` Notificaciones · `TC-PERFIL-xxx` Perfil · `TC-ADMIN-xxx` Consola admin · `TC-ERR-xxx` Errores/edge cases · `TC-MULTI-xxx` Multi-usuario/concurrencia · `TC-REG-xxx` Regresión · `TC-E2E-xxx` Flujos E2E completos · `TC-EDGE-xxx` Casos borde.

---

## 2. Matriz de pruebas por módulos y flujos

### 2.1 Autenticación y registro

| ID | Módulo | Escenario | Pasos a ejecutar | Resultado esperado (UI y Backend) | Estado | Comentarios / Logs de Fallo |
|---|---|---|---|---|---|---|
| TC-AUTH-001 | Login | Login exitoso GM | 1. Ir a `/login`<br>2. Email `gm@tfinder.dev`, pass `DemoTFinder123!`<br>3. Presionar "Ingresar" | Redirect a `/feed`. Header muestra iniciales y dropdown "Mis campañas". Sin errores de consola. | `[ ]` | |
| TC-AUTH-002 | Login | Login exitoso jugador | 1. `/login`<br>2. `navuno@tfinder.dev` / `Navegador1!`<br>3. Ingresar | Redirect a `/feed`. Nav muestra "Mis mesas" (no "Mis campañas" si no es GM). | `[ ]` | |
| TC-AUTH-003 | Login | Credenciales inválidas | 1. `/login`<br>2. Email válido + contraseña incorrecta<br>3. Ingresar | Toast/error "Credenciales inválidas". Permanece en `/login`. Sin redirect. | `[ ]` | |
| TC-AUTH-004 | Login | Email con formato inválido | 1. Ingresar email sin `@`<br>2. Presionar Ingresar | Validación inline "El correo electrónico no tiene un formato válido". Botón no envía. | `[ ]` | |
| TC-AUTH-005 | Login | Campos vacíos | 1. Presionar "Ingresar" con todo vacío | Mensajes "El email es obligatorio" / "La contraseña es obligatoria". Sin request de red. | `[ ]` | |
| TC-AUTH-006 | Login | Persistencia de sesión | 1. Login exitoso<br>2. Recargar `/feed` (F5) | Sigue autenticado, sin redirect a login. | `[ ]` | |
| TC-AUTH-007 | Login | Logout desde el menú | 1. Autenticado → header "Menú" → "Cerrar sesión" | Sesión limpiada, redirect `/`. Header vuelve a invitado. | `[ ]` | |
| TC-AUTH-008 | Registro | Registro exitoso jugador | 1. `/registro`<br>2. Nombre, email nuevo, contraseña ≥8, aceptar términos<br>3. "Crear cuenta" | Redirect a `/feed`. Sesión activa con rol jugador. | `[ ]` | |
| TC-AUTH-009 | Registro | Registro sin aceptar términos | 1. Completar datos<br>2. NO marcar checkbox<br>3. "Crear cuenta" | Error "Falta aceptar los términos." Sin request. | `[ ]` | |
| TC-AUTH-010 | Registro | Contraseña corta | 1. Password de 5 caracteres | Validación "La contraseña debe tener al menos 8 caracteres." | `[ ]` | |
| TC-AUTH-011 | Registro | Email duplicado | 1. Registrar email ya existente | Error "El correo ya está registrado" (409). | `[ ]` | |
| TC-AUTH-012 | Recuperación | Solicitar recuperación | 1. `/recuperar`<br>2. Email válido<br>3. Enviar | Mensaje "Si el correo existe, enviamos un enlace." (no revela existencia). 202 del backend. | `[ ]` | |
| TC-AUTH-013 | Recuperación | Email inválido | 1. `/recuperar`<br>2. Email sin `@` | Validación inline. Sin request. | `[ ]` | |
| TC-AUTH-014 | Sesión | Token expirado (simulado) | 1. Modificar `access_token` en localStorage a un valor inválido<br>2. Navegar a `/mis-mesas` | Redirect a `/login?redirect=/mis-mesas`. (Idealmente con banner "Tu sesión venció".) | `[ ]` | |
| TC-AUTH-015 | Logout móvil | Cerrar sesión desde panel móvil | 1. Auth → hamburguesa → "Cerrar sesión" | Sesión limpiada, redirect `/`. Panel se cierra. | `[ ]` | |

### 2.2 Perfil de usuario

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-PERFIL-001 | Perfil | Ver perfil propio | 1. Autenticado → `/perfil` | Muestra nombre, iniciales, título, email, bio (si existe). | `[ ]` | |
| TC-PERFIL-002 | Perfil | Editar nombre/bio | 1. Editar campos<br>2. Guardar | Toast "Perfil actualizado". Refleja en header (iniciales). | `[ ]` | |
| TC-PERFIL-003 | Perfil | Cambiar contraseña | 1. Contraseña actual + nueva (≥8)<br>2. Guardar | Toast éxito. Re-login con la nueva contraseña funciona. | `[ ]` | |
| TC-PERFIL-004 | Perfil | Contraseña actual incorrecta | 1. Actual incorrecta | Error "Contraseña actual incorrecta". Sin cambio. | `[ ]` | |
| TC-PERFIL-005 | Perfil | Subir avatar | 1. Seleccionar imagen<br>2. Confirmar | Avatar actualizado en perfil y header. | `[ ]` | |
| TC-PERFIL-006 | Perfil | Eliminar avatar | 1. "Eliminar avatar" | Vuelve al avatar por defecto (iniciales). | `[ ]` | |
| TC-PERFIL-007 | Perfil | Subida de archivo inválido (no imagen) | 1. Subir `.txt` o >5MB | Error "Formato/tamaño no soportado". Sin upload. | `[ ]` | |

### 2.3 Navegación y layout

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-NAV-001 | Layout | Header por rol (invitado) | 1. Abrir `/` sin sesión | Nav: "Explorar mesas", "Feed", "Iniciar sesión", "Crear cuenta". Sin "Mis mesas". | `[ ]` | |
| TC-NAV-002 | Layout | Header por rol (jugador) | 1. Login jugador | Nav: "Explorar mesas", "Feed", "Mis mesas", "Builds", "Notificaciones", avatar, "Menú" con "Cerrar sesión". | `[ ]` | |
| TC-NAV-003 | Layout | Header por rol (GM) | 1. Login GM | Dropdown "Mis campañas" visible si tiene mesas. | `[ ]` | |
| TC-NAV-004 | Layout | Header por rol (admin) | 1. Login admin | Enlaces de consola admin visibles. | `[ ]` | |
| TC-NAV-005 | Layout | Menú móvil abre/cierra | 1. Viewport móvil (<1024px)<br>2. Tocar hamburguesa | Panel móvil se abre con nav y "Cerrar sesión". Toggle cierra. | `[ ]` | |
| TC-NAV-006 | Layout | Landing con sesión | 1. Autenticado → `/` | Nav muestra perfil + "Cerrar sesión" (no "Iniciar sesión" fijo). | `[ ]` | |
| TC-NAV-007 | Layout | Landing sin enlaces muertos | 1. `/` invitado | Sin `/bestiario`, `/compendio`. "Mesas abiertas" y `/feed` resuelven. | `[ ]` | |
| TC-NAV-008 | Layout | Footer sin enlace índice | 1. Footer de cualquier página | Sin "todas las pantallas" (`/indice`). "Mesas", "comunidades" resuelven. | `[ ]` | |
| TC-NAV-009 | Layout | Guard invita → login | 1. Invitado → `/mesas/nueva` | Redirect a `/login?redirect=/mesas/nueva`. | `[ ]` | |
| TC-NAV-010 | Layout | Guard jugador → /mesas | 1. Jugador → `/admin` | Redirect a `/mesas`. | `[ ]` | |
| TC-NAV-011 | Layout | Guard GM → /mesas | 1. Jugador → `/mesas/1/gestion` | Toast "No sos integrante…" + redirect `/mesas`. | `[ ]` | |
| TC-NAV-012 | Layout | Pull-to-refresh / red | 1. Desconectar red<br>2. Navegar | Estados de error ("No se pudo cargar"). Sin crash. Al reconectar, reintentar carga. | `[ ]` | |
| TC-NAV-013 | Layout | 404 NotFound | 1. `/ruta-inexistente` | Vista "Esta cripta está vacía" con link a `/mesas`. | `[ ]` | |
| TC-NAV-014 | Layout | Responsive breakpoints | 1. Viewport 360px, 768px, 1024px, 1440px | Sin overflow horizontal; tabs scrollean; modales centrados. | `[ ]` | |

### 2.4 Catálogo de mesas y detalle

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-MESA-001 | Catálogo | Listado público | 1. `/mesas` sin sesión | Mesas abiertas visibles con nombre, GM, horario, cupo. | `[ ]` | |
| TC-MESA-002 | Catálogo | Filtro por estado | 1. `/mesas?estado=cerrada` | Solo mesas cerradas. | `[ ]` | |
| TC-MESA-003 | Catálogo | Paginación | 1. Cambiar página/limit | Carga siguiente bloque sin duplicar. | `[ ]` | |
| TC-MESA-004 | Catálogo | Estado vacío | 1. Filtro que no matchee | "No hay mesas abiertas" con CTA "Publicá tu campaña". | `[ ]` | |
| TC-MESA-005 | Detalle | Mesa existente (invitado) | 1. Invitado → `/mesas/1` | Ficha pública visible. Pestaña "Personajes" vacía (sin "Mesa no encontrada"). | `[ ]` | |
| TC-MESA-006 | Detalle | Mesa inexistente | 1. `/mesas/99999` | "Mesa no encontrada" + link "Ver las mesas abiertas". | `[ ]` | |
| TC-MESA-007 | Detalle | Mesa cerrada | 1. `/mesas/3` (demo cerrada) | Tag "Cerrada", botón "Solicitar unión" deshabilitado. | `[ ]` | |
| TC-MESA-008 | Detalle | Mesa completa | 1. Mesa con jugadores == cupo | Tag "Completa", botón deshabilitado. | `[ ]` | |
| TC-MESA-009 | Detalle | Solicitar unión (jugador) | 1. Autenticado no-miembro → "Solicitar unión" | Toast "Solicitud enviada". Tag "Solicitud enviada". | `[ ]` | |
| TC-MESA-010 | Detalle | Ya miembro | 1. Miembro → `/mesas/1` | Tag "Ya eres miembro". | `[ ]` | |
| TC-MESA-011 | Detalle | Deslogueado solicita unión | 1. Invitado → "Solicitar unión" | Redirect a `/login?redirect=/mesas/1`. | `[ ]` | |
| TC-MESA-012 | Detalle | Link Wiki de campaña | 1. "Wiki de la campaña" | Navega a `/wiki`. | `[ ]` | |
| TC-MESA-013 | Mesas (multi) | Flujo completo creación + postulación | 1. GM crea mesa "Mesa E2E Unión" (cupo 2)<br>2. Jugador 1 solicita unión<br>3. Jugador 2 solicita unión<br>4. GM acepta J1 y rechaza J2<br>5. J1 ve la mesa en `/mis-mesas` (tag "Ya eres miembro")<br>6. J2 sigue pudiendo solicitar unión<br>7. GM expulsa a J1 → J1 deja de ser miembro | POST solicitudes ×2 (201); aceptar (200, miembro creado); rechazar (200); ocupación 0→1→0; notificaciones cruzadas (J1 "Solicitud aceptada", GM "Nueva solicitud" ×2). | `[ ]` | |
| TC-MESA-013a | Mesas (multi) | Cupo lleno | 1. Mesa con 2/2 jugadores<br>2. Tercer jugador solicita unión | Backend 409 "Sin cupo disponible" (o pendiente sin poder aceptarse). Sin superar cupo. | `[ ]` | |
| TC-MESA-013b | Mesas (multi) | Doble solicitud | 1. Mismo jugador envía dos solicitudes | 409 "Ya tenés una solicitud activa". | `[ ]` | |
| TC-MESA-013c | Mesas (multi) | Solicitud a mesa cerrada | 1. Mesa en estado cerrada<br>2. Jugador solicita | 409 "La mesa está cerrada". | `[ ]` | |
| TC-MESA-013d | Mesas (multi) | Aceptar sin cupo | 1. Cupo 0/2, solicitud pendiente<br>2. GM acepta | 409 y no consume plaza. | `[ ]` | |
| TC-MESA-013e | Mesas (multi) | No propietario acepta/rechaza | 1. Jugador intenta aceptar solicitud ajena | 403. | `[ ]` | |
| TC-MESA-013f | Mesas (multi) | Rate limit con varios usuarios | 1. 3 usuarios postulándose en secuencia rápida | Sin 429 indebidamente (cada uno su cupo por XFF). | `[ ]` | |

### 2.5 Crear y editar mesa

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-CREAR-001 | Crear | Formulario completo | 1. `/mesas/nueva` (auth)<br>2. Nombre ≥4, nivel, cupo, ambientación libre, horario, descripción<br>3. "Publicar mesa" | POST con `tono=ambientación`. Redirect a `/mis-mesas-gm`. Mesa en listado. | `[ ]` | |
| TC-CREAR-002 | Crear | Nombre vacío | 1. Submit sin nombre | "El nombre de la mesa es obligatorio". Sin request. | `[ ]` | |
| TC-CREAR-003 | Crear | Nombre corto (<4) | 1. Nombre "abc" | "El nombre necesita 4 o más caracteres." | `[ ]` | |
| TC-CREAR-004 | Crear | Nivel inválido | 1. Nivel 0 o >20 | "El nivel inicial debe ser un entero positivo." | `[ ]` | |
| TC-CREAR-005 | Crear | Cupo inválido | 1. Cupo 0 o negativo | "El cupo máximo debe ser un entero mayor a cero." | `[ ]` | |
| TC-CREAR-006 | Crear | Ambientación libre (no select) | 1. Escribir texto libre en ambientación | Persiste en `tono` al ver detalle. No se envía `lugar`. | `[ ]` | |
| TC-CREAR-007 | Crear | Invitado crea mesa | 1. Invitado → `/mesas/nueva` | Redirect a login. | `[ ]` | |
| TC-CREAR-008 | Editar | Carga de mesa existente | 1. `/mesas/1/editar` (GM) | Campos pre-poblados con datos reales; horario sin "A coordinar". | `[ ]` | |
| TC-CREAR-009 | Editar | Guardar cambios | 1. Cambiar nombre/horario/cupo → "Guardar" | PUT con `frecuencia→horario`. Toast éxito. Redirect a `/mesas/1/gestion`. | `[ ]` | |
| TC-CREAR-010 | Editar | Cupo menor a jugadores actuales | 1. Cupo < jugadores actuales | Error 409 "El cupo máximo no puede ser menor…" | `[ ]` | |
| TC-CREAR-011 | Editar | No propietario edita | 1. Jugador → `/mesas/1/editar` | 403 / "Esta mesa no es tuya". | `[ ]` | |

### 2.6 Panel GM y gestión de campaña

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-GM-001 | Panel GM | Acceso GM propio | 1. GM → `/mesas/1/gm` | Panel visible con métricas, bandeja, edición. | `[ ]` | |
| TC-GM-002 | Panel GM | No propietario | 1. Jugador → `/mesas/1/gm` | "Esta mesa no es tuya" (VAL-17). | `[ ]` | |
| TC-GM-003 | Panel GM | Cupo real | 1. Panel de mesa con 2/4 jugadores | "2/4" y "2 vacantes" (sin undefined/NaN). | `[ ]` | |
| TC-GM-004 | Panel GM | Toggle estado | 1. "Cerrar mesa" → "Reabrir mesa" | Tag cambia; PUT estado `cerrada`/`abierta`. | `[ ]` | |
| TC-GM-005 | Panel GM | Guardar edición | 1. Editar nombre/horario/cupo → "Guardar cambios" | PUT con `jugadores_max`. Toast éxito. | `[ ]` | |
| TC-GM-006 | Panel GM | Bandeja de solicitudes | 1. Vista con solicitudes pendientes | Lista con nombre + nota. Aceptar/Rechazar visibles. | `[ ]` | |
| TC-GM-007 | Panel GM | Aceptar solicitud | 1. "Aceptar" | Toast éxito. Solicitud desaparece. Ocupación +1. | `[ ]` | |
| TC-GM-008 | Panel GM | Rechazar solicitud | 1. "Rechazar" | Toast. Solicitud desaparece. | `[ ]` | |
| TC-GM-009 | Panel GM | Expulsar miembro | 1. "Expulsar" → confirmar | Miembro removido. Ocupación -1. | `[ ]` | |
| TC-GM-010 | Panel GM | Invitar jugador | 1. "Invitar jugador" | Toast "Enlace copiado (simulado)". | `[ ]` | |
| TC-GM-011 | Panel GM | Modo sesión | 1. "Modo sesión" | Navega a `/mesas/1/sesion`. | `[ ]` | |
| TC-GES-001 | Gestión shell | Carga parcial | 1. GM → `/mesas/1/gestion` con un endpoint secundario caído | Mesa visible con tabs; sección afectada degrada (no "Mesa no encontrada"). | `[ ]` | |
| TC-GES-002 | Gestión shell | Tabs visibles por feature | 1. Revisar tabs | Solo tabs habilitadas (Resumen, Wiki, Calendario, Sesiones, Jugadores, Builds). | `[ ]` | |
| TC-GES-003 | Gestión shell | Contador de pestañas | 1. Ver tabs | Wiki count, Sesiones count, Jugadores `x/y`. | `[ ]` | |
| TC-GES-004 | Gestión shell | Menú móvil en gestión | 1. Viewport móvil | Hamburguesa abre panel; cerrar sesión visible. | `[ ]` | |

### 2.7 Calendario y votación

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-CAL-001 | Calendario (GM) | Ver calendario | 1. `/mesas/1/gestion/calendario` | Cuadrícula del mes con días; propuestas listadas. | `[ ]` | |
| TC-CAL-002 | Calendario (GM) | Proponer fecha | 1. "Proponer fecha" → día + hora → "Convocar" | POST con `propuesta: YYYY-MM-DDTHH:mm:00` (ISO válido). Propuesta aparece. Toast éxito. | `[ ]` | |
| TC-CAL-003 | Calendario (GM) | Proponer sin fecha | 1. Submit vacío | Error "Elegí una fecha con el selector." | `[ ]` | |
| TC-CAL-004 | Calendario (GM) | Hora por defecto 20:00 | 1. Proponer solo fecha | ISO termina en `T20:00:00`. | `[ ]` | |
| TC-CAL-005 | Calendario (GM) | Marca por fecha real | 1. Mes con sesión/propuesta | Celda del día muestra "SESIÓN"/"PROPUESTA" (no solo sábados). | `[ ]` | |
| TC-CAL-006 | Calendario (GM) | Capacidad real | 1. Ver quórum | "quórum actual es de X de Y" (sin "de null"). | `[ ]` | |
| TC-CAL-007 | Calendario (GM) | Mes anterior/siguiente | 1. « / » | Cambia mes/año correctamente. | `[ ]` | |
| TC-CAL-008 | Calendario (jugador) | Votar a favor | 1. Jugador → `/mesas/1/calendario` → ▲ | Voto registrado. Contador +1. `aria-pressed=true`. | `[ ]` | |
| TC-CAL-009 | Calendario (jugador) | Votar en contra | 1. ▼ | Voto "en contra". | `[ ]` | |
| TC-CAL-010 | Calendario (jugador) | Cambiar voto | 1. Votar favor → en contra | Voto actualizado (no duplicado). | `[ ]` | |
| TC-CAL-011 | Calendario (jugador) | GM no vota | 1. GM intenta votar | 403 "El GM no vota las fechas que propone." | `[ ]` | |
| TC-CAL-012 | Calendario (GM) | Confirmar fecha | 1. "Confirmar fecha" | Fecha pasa a confirmada; crea sesión. Toast. | `[ ]` | |
| TC-CAL-013 | Calendario (GM) | Descartar fecha | 1. "Descartar" | Propuesta removida. | `[ ]` | |
| TC-CAL-014 | Calendario (jugador) | Voto propio visible | 1. Login jugador que ya votó → calendario | Su voto aparece marcado (aria-pressed) con `mi_voto` real. | `[ ]` | |
| TC-CAL-015 | Calendario | Sin propuestas | 1. Mesa sin propuestas | "No hay propuestas abiertas…" | `[ ]` | |

### 2.8 Sesiones, bitácora y diario

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-SES-001 | Sesiones | Listado real | 1. `/mesas/1/gestion/sesiones` | Filas por fecha real. Estados ABIERTA/CERRADA. Sin TypeError con ≥2 sesiones. | `[ ]` | |
| TC-SES-002 | Sesiones | Orden cronológico | 1. Ver listado | Más reciente arriba. | `[ ]` | |
| TC-SES-003 | Sesiones | Enlaces QR/bitácora/diario | 1. Click "Asistencia (QR)" / "Bitácora" / "Diario" | Navegan a `/gestion/sesiones/:id/qr|bitacora|diario` (no 404). | `[ ]` | |
| TC-SES-004 | Sesiones | QR solo en abiertas | 1. Sesión cerrada | Sin botón QR; con "Diario de sesión". | `[ ]` | |
| TC-SES-005 | Sesiones | Vacío | 1. Mesa sin sesiones | "Aún no hay sesiones convocadas…" | `[ ]` | |
| TC-SES-006 | QR | Generar QR | 1. `/mesas/1/gestion/sesiones/3/qr` | QR PNG visible. TTL 600s. Cuenta regresiva. | `[ ]` | |
| TC-SES-007 | QR | Vencimiento | 1. Esperar a 0s | Botón "Generar otro QR" habilitado. | `[ ]` | |
| TC-SES-008 | QR | Validar asistencia (GM) | 1. Pegar qr_data → "Validar asistencia" | "Asistencia registrada". Single-use. | `[ ]` | |
| TC-SES-009 | QR | QR vencido/usado | 1. Validar QR ya usado | "QR vencido o ya utilizado (409 single-use)". | `[ ]` | |
| TC-SES-010 | QR | QR inválido | 1. Pegar texto sin identificador | "El qr_data pegado no contiene el identificador de jugador." | `[ ]` | |
| TC-SES-011 | Bitácora | Listar anotaciones | 1. `/mesas/1/gestion/sesiones/3/bitacora` | Lista cronológica con autor. | `[ ]` | |
| TC-SES-012 | Bitácora | Anotación vacía | 1. Submit con espacios | Error "El texto no puede estar vacío". Sin POST. | `[ ]` | |
| TC-SES-013 | Bitácora | Registrar anotación | 1. Texto válido → submit | POST y refresco de lista. | `[ ]` | |
| TC-SES-014 | Diario | Editar diario | 1. `/mesas/1/gestion/sesiones/3/diario` | Formulario con título, XP/tesoro, resumen, asistencia. | `[ ]` | |
| TC-SES-015 | Diario | Guardar diario vacío | 1. Submit sin resumen | Error "El resumen no puede quedar en blanco." | `[ ]` | |
| TC-SES-016 | Diario | Guardar diario | 1. Completar → "Guardar diario" | POST con cuerpo. Toast éxito. Redirect a sesiones. | `[ ]` | |
| TC-SES-017 | Modo sesión | Modo GM | 1. `/mesas/1/sesion` | Bitácora del modo sesión. | `[ ]` | |
| TC-SES-018 | Modo sesión | Modo jugador | 1. `/mesas/1/sesion/jugador` | "Bitácora de la sesión (jugador)". | `[ ]` | |

### 2.9 Wiki colaborativa

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-WIKI-001 | Wiki | Índice | 1. `/mesas/1/gestion/wiki` | Carpetas con contador; páginas listadas. | `[ ]` | |
| TC-WIKI-002 | Wiki | Filtrar por tipo | 1. Cambiar filtro LUGARES/PERSONAJES/… | Solo páginas del tipo. | `[ ]` | |
| TC-WIKI-003 | Wiki | Buscar | 1. Buscar por título/resumen | Filtrado en vivo. | `[ ]` | |
| TC-WIKI-004 | Wiki | Crear página | 1. "Crear página" → completar → "Guardar" | Página creada. Redirect a lectura. | `[ ]` | |
| TC-WIKI-005 | Wiki | Crear sin título | 1. Submit sin título | Error "El título de la página es obligatorio." | `[ ]` | |
| TC-WIKI-006 | Wiki | Editar página | 1. `/mesas/1/wiki/:id/editar` | Campos pre-poblados. Guardar → redirect a lectura. | `[ ]` | |
| TC-WIKI-007 | Wiki | Eliminar página | 1. "Eliminar página" → confirmar | Página removida del índice. | `[ ]` | |
| TC-WIKI-008 | Wiki | Lectura | 1. `/mesas/1/wiki/:id` | Contenido renderizado (párrafos, subtítulos, listas, citas). | `[ ]` | |
| TC-WIKI-009 | Wiki | Contribuciones | 1. Enviar contribución como jugador | Pendiente de aprobación. | `[ ]` | |
| TC-WIKI-010 | Wiki | Aprobar/rechazar contribución | 1. GM → aprobar/rechazar | Estado actualizado. | `[ ]` | |

### 2.10 Jugadores y solicitudes

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-JUG-001 | Jugadores | Bandeja con solicitudes | 1. `/mesas/1/gestion/jugadores` | Solicitudes pendientes con nombre/rol/nota. | `[ ]` | |
| TC-JUG-002 | Jugadores | Aceptar | 1. "Aceptar" | Solicitud se mueve a miembros. Ocupación +1. | `[ ]` | |
| TC-JUG-003 | Jugadores | Rechazar | 1. "Rechazar" | Solicitud removida. | `[ ]` | |
| TC-JUG-004 | Jugadores | Expulsar | 1. "Expulsar" → confirmar | Miembro removido. Ocupación -1. | `[ ]` | |
| TC-JUG-005 | Jugadores | Capacidad real | 1. Ver miembros | "x/y plazas" con rol real (Master/Jugador), sin undefined. | `[ ]` | |
| TC-JUG-006 | Jugadores | Sin miembros | 1. Mesa nueva | "Sin miembros aún." | `[ ]` | |
| TC-JUG-007 | Solicitudes GM | Bandeja global | 1. `/solicitudes-gm` | Solicitudes pendientes de todas las mesas del GM. | `[ ]` | |

### 2.11 Builds (PF1e)

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-BUILD-001 | Builds | Listado público | 1. `/builds` (pestaña "Públicos") | Builds publicados visibles. | `[ ]` | |
| TC-BUILD-002 | Builds | Mis builds | 1. Pestaña "Mis builds" | Builds propios (incl. borradores) visibles. | `[ ]` | |
| TC-BUILD-003 | Builds | Wizard de creación | 1. `/builds/asistente` → completar → "Publicar Ficha" | Build creado y redirect a detalle. | `[ ]` | |
| TC-BUILD-004 | Builds | Detalle con ficha | 1. `/builds/:id` | Atributos, dotes, conjuros, defensa/ataque renderizados. | `[ ]` | |
| TC-BUILD-005 | Builds | Detalle sin ficha | 1. Build borrador sin ficha | "La ficha OGL completa… aún no se ha publicado." | `[ ]` | |
| TC-BUILD-006 | Builds | Editar build | 1. `/builds/:id/editar` | Formulario con datos; guardar → redirect detalle. | `[ ]` | |
| TC-BUILD-007 | Builds | Historial/versionado | 1. `/builds/:id/historial` | Versiones listadas. | `[ ]` | |
| TC-BUILD-008 | Builds | Vincular a mesa | 1. "Asociar mi Build" → elegir mesa | Toast "Build vinculado". Aparece en la pestaña Builds de la mesa. | `[ ]` | |
| TC-BUILD-009 | Builds | Publicar en feed | 1. "Publicar en Feed" (build público) | Publicación creada en feed. | `[ ]` | |
| TC-BUILD-010 | Builds | Publicar build privado | 1. Build borrador → "Publicar en Feed" | Error "Solo los builds públicos…". | `[ ]` | |
| TC-BUILD-011 | Builds | Agregar a wiki | 1. "Agregar a Wiki" (build vinculado a mesa) | Página de wiki creada. | `[ ]` | |
| TC-BUILD-012 | Builds | Agregar a wiki sin mesa | 1. Build sin mesa → "Agregar a Wiki" | Error "Vinculá el build a una mesa primero…" | `[ ]` | |
| TC-BUILD-013 | Builds | Fork de build | 1. "Fork" en detalle | Nuevo build creado. Redirect a edición. | `[ ]` | |
| TC-BUILD-014 | Builds | /builds/nuevo (ruta) | 1. Navegar a `/builds/nuevo` | *(Conocido)* colisiona con `/builds/:id` → muestra detalle inexistente. Debe redirigir a `/builds/asistente`. | `[ ]` | Defecto conocido |

### 2.12 Feed social

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-FEED-001 | Feed | Listado | 1. `/feed` autenticado | Posts ordenados (hot). | `[ ]` | |
| TC-FEED-002 | Feed | Composer (autenticado) | 1. `/feed` autenticado | Botón "Publicar" visible. | `[ ]` | |
| TC-FEED-003 | Feed | Publicar post | 1. Escribir + "Publicar" | Post aparece en el feed. | `[ ]` | |
| TC-FEED-004 | Feed | Invitado publica | 1. Invitado → `/feed` | Sin composer. | `[ ]` | |
| TC-FEED-005 | Feed | Like | 1. Like en un post | Contador +1. | `[ ]` | |
| TC-FEED-006 | Feed | Comunidades | 1. `/feed?comunidad=x` | Filtro por comunidad. | `[ ]` | |
| TC-FEED-007 | Feed | Sin posts | 1. Feed vacío | Estado vacío amable. | `[ ]` | |

### 2.13 Encuentros y tags

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-ENC-001 | Encuentros | Generar (Desafiante) | 1. `/encuentros` → "Desafiante" → "Lanzar encuentro" | Grupo de criaturas + CR + XP. Toast con resumen. | `[ ]` | |
| TC-ENC-002 | Encuentros | Generar (Trivial/Épica) | 1. Cambiar dificultad | Meta XP ajustada. | `[ ]` | |
| TC-ENC-003 | Encuentros | Añadir a sesión | 1. "Añadir a la sesión" | Toast éxito. Redirect `/mis-mesas`. | `[ ]` | |
| TC-ENC-004 | Encuentros | Guardar en bestiario | 1. "Guardar en bestiario" | Toast éxito. | `[ ]` | |
| TC-TAG-001 | Tags | Crear tag | 1. `/tags` → nombre → "Crear tag" | Tag agregado. Toast. | `[ ]` | |
| TC-TAG-002 | Tags | Tag duplicado | 1. Crear tag existente | Toast "El tag ya existe." | `[ ]` | |
| TC-TAG-003 | Tags | Tag vacío | 1. Submit vacío | Toast "Escribí un nombre…" | `[ ]` | |
| TC-TAG-004 | Tags | Aplicar tag | 1. Click en tag | Toggle ✓/+. Contador actualizado. | `[ ]` | |

### 2.14 Notificaciones

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-NOTIF-001 | Notificaciones | Listado | 1. `/notificaciones` | Notificaciones con mensaje, detalle, fecha. | `[ ]` | |
| TC-NOTIF-002 | Notificaciones | Marcar leída | 1. Click en notificación | `leida=true`. Badge decrementa. | `[ ]` | |
| TC-NOTIF-003 | Notificaciones | Marcar todas leídas | 1. "Marcar todas" | Badge 0. | `[ ]` | |
| TC-NOTIF-004 | Notificaciones | Badge en header | 1. Notificaciones no leídas | Badge numérico visible. | `[ ]` | |
| TC-NOTIF-005 | Notificaciones | Panel campana | 1. Click 🔔 | Últimas 5 + "Ver todas". | `[ ]` | |
| TC-NOTIF-006 | Notificaciones | Enlace válido | 1. Click en notificación con enlace | Navega a ruta real (no NotFound). | `[ ]` | |
| TC-NOTIF-007 | Notificaciones | Enlace muerto (legacy) | 1. Notificación vieja `/mesas/demo` | Redirige a `/mesas` (no "Mesa no encontrada"). | `[ ]` | |
| TC-NOTIF-008 | Notificaciones | Sin notificaciones | 1. Usuario sin notifs | "Silencio: nada sin leer." | `[ ]` | |
| TC-NOTIF-009 | Notificaciones | Stream (SSE) | 1. Mantener pestaña abierta + evento backend | Notificación aparece en tiempo real. | `[ ]` | |

### 2.15 Consola admin (solo rol admin)

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-ADMIN-001 | Admin | Acceso admin | 1. Login admin → `/admin` | Panel con 3 cards (eventos, DLQ, emails). | `[ ]` | |
| TC-ADMIN-002 | Admin | Acceso no-admin | 1. Login jugador → `/admin` | Redirect a `/mesas`. Toast "La consola es de administradores". | `[ ]` | |
| TC-ADMIN-003 | Admin | Event log | 1. `/admin/eventos` | Tabla con id, entidad, acción, usuario, correlación, fecha. | `[ ]` | |
| TC-ADMIN-004 | Admin | DLQ listar | 1. `/admin/dlq` | Mensajes con cola y error. Botones "Reintentar"/"Descartar". | `[ ]` | |
| TC-ADMIN-005 | Admin | DLQ reintentar | 1. "Reintentar" | POST `/dlq/:id/reintentar`. Mensaje removido. Toast. | `[ ]` | |
| TC-ADMIN-006 | Admin | DLQ descartar | 1. "Descartar" | DELETE `/dlq/:id`. Mensaje removido. | `[ ]` | |
| TC-ADMIN-007 | Admin | DLQ vacía | 1. Sin mensajes | "La cola de muertos está vacía." | `[ ]` | |
| TC-ADMIN-008 | Admin | Emails | 1. `/admin/emails` | Tabla con destino, asunto, estado, error. | `[ ]` | |
| TC-ADMIN-009 | Admin | Reintentar email | 1. "Reintentar" en email fallido | POST `/emails/:id/reintentar`. Estado actualizado. | `[ ]` | |
| TC-ADMIN-010 | Admin | Bootstrap admin | 1. `python scripts/bootstrap_admin.py` | Crea admin en mesas_db. Login exitoso. | `[ ]` | |

### 2.16 Gestión de errores y casos límite

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-ERR-001 | Offline | Sin conexión al cargar | 1. Desconectar red → `/mesas` | Estado de error con "Reintentar". Sin crash. | `[ ]` | |
| TC-ERR-002 | Offline | Reintentar tras reconexión | 1. Reconectar → "Reintentar" | Carga exitosa. | `[ ]` | |
| TC-ERR-003 | Offline | Submit con red caída | 1. Crear mesa sin red | Error toast. Datos del formulario se conservan. | `[ ]` | |
| TC-ERR-004 | Backend 4xx | 400 validación | 1. Enviar payload inválido | Mensaje de validación específico. | `[ ]` | |
| TC-ERR-005 | Backend 4xx | 403 membresía | 1. No-miembro → `/mesas/1/gestion` | Toast "No sos integrante…" + redirect `/mesas`. | `[ ]` | |
| TC-ERR-006 | Backend 4xx | 404 mesa | 1. `/mesas/99999` | "Mesa no encontrada" + link. | `[ ]` | |
| TC-ERR-007 | Backend 4xx | 409 cupo | 1. Bajar cupo por debajo de jugadores | Error 409 con mensaje. | `[ ]` | |
| TC-ERR-008 | Backend 429 | Rate limit | 1. Navegar rápido (>20 llamadas/min desde la misma IP) | *(Conocido)* respuestas 429. Idealmente aviso "servidor ocupado" (hoy se muestra como "no encontrada/vacío"). | `[ ]` | Defecto conocido |
| TC-ERR-009 | Backend 5xx | Servicio caído | 1. Detener mesas-api → `/mesas` | Error de conexión. Circuit breaker abre tras 5 fallos. | `[ ]` | |
| TC-ERR-010 | Timeout | Backend lento | 1. Simular latencia >8s | Timeout con mensaje. Sin spinner infinito. | `[ ]` | |
| TC-ERR-011 | Inputs | Caracteres especiales | 1. Nombre con `<script>`, emojis, acentos | Sanitizado/aceptado sin XSS. | `[ ]` | |
| TC-ERR-012 | Inputs | Campos con espacios | 1. Nombre "   " | Validación "obligatorio". | `[ ]` | |
| TC-ERR-013 | Sesión | Token inválido | 1. Falsificar `access_token` → navegar | Redirect a `/login` (idealmente con banner "Tu sesión venció"). | `[ ]` | |
| TC-ERR-014 | Sesión | Renovación de token | 1. Forzar 401 con token vencido pero refresh válido | Renovación silenciosa. Sin redirect. | `[ ]` | |
| TC-ERR-015 | Rate limit | Varios usuarios misma IP | 1. Dos browsers desde la misma red | *(Corregido)* cada uno su propio cupo (XFF). Antes compartían. | `[ ]` | Verificar |

### 2.17 Visual y UX

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-UX-001 | Visual | Tema global | 1. Navegar landing, mesas, gestión | Tema arcade oscuro (mint/rosa). Sin pergamino global. | `[ ]` | |
| TC-UX-002 | Visual | Skeleton screens | 1. Carga lenta | Skeletons en lugar de pantallas vacías. | `[ ]` | |
| TC-UX-003 | Visual | Spinners | 1. Acciones async | Spinner en botones (disabled). | `[ ]` | |
| TC-UX-004 | Visual | Toasters | 1. Acciones exitosas/fallidas | Toast visible, se auto-cierra (~3.2s). | `[ ]` | |
| TC-UX-005 | Visual | Estados vacíos | 1. Listas sin datos | Mensaje amable + CTA. | `[ ]` | |
| TC-UX-006 | Visual | Modales | 1. Abrir/cerrar modales (ConfirmModal, BaseModal) | Overlay, foco atrapado, cierre con ESC/click fuera. | `[ ]` | |
| TC-UX-007 | Visual | Responsive 360px | 1. Viewport 360×640 | Sin overflow horizontal. Tabs scrollean. | `[ ]` | |
| TC-UX-008 | Visual | Responsive 768px | 1. Viewport 768×1024 | Layout a 2 columnas donde corresponda. | `[ ]` | |
| TC-UX-009 | Visual | Accesibilidad | 1. Navegar con teclado (Tab/Enter/Esc) | Foco visible. ARIA labels en botones icono. | `[ ]` | |
| TC-UX-010 | Visual | Contraste | 1. Inspeccionar textos | Contraste suficiente (WCAG AA). | `[ ]` | |

### 2.18 Pruebas multi-usuario / concurrencia

| ID | Módulo | Escenario | Pasos a ejecutar | Resultado esperado (UI y Backend) | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-MESA-013 | Mesas (multi) | Flujo completo creación + postulación | 1. GM crea mesa "Mesa E2E Unión" (cupo 2)<br>2. Jugador 1 solicita unión<br>3. Jugador 2 solicita unión<br>4. GM acepta J1 y rechaza J2<br>5. J1 ve la mesa en `/mis-mesas` (tag "Ya eres miembro")<br>6. J2 sigue pudiendo solicitar unión<br>7. GM expulsa a J1 → J1 deja de ser miembro | POST solicitudes ×2 (201); aceptar (200, miembro creado); rechazar (200); ocupación 0→1→0; notificaciones cruzadas (J1 "Solicitud aceptada", GM "Nueva solicitud" ×2). | `[ ]` | |
| TC-MESA-013a | Mesas (multi) | Cupo lleno | 1. Mesa con 2/2 jugadores<br>2. Tercer jugador solicita unión | Backend 409 "Sin cupo disponible" (o pendiente sin poder aceptarse). Sin superar cupo. | `[ ]` | |
| TC-MESA-013b | Mesas (multi) | Doble solicitud | 1. Mismo jugador envía dos solicitudes | 409 "Ya tenés una solicitud activa". | `[ ]` | |
| TC-MESA-013c | Mesas (multi) | Solicitud a mesa cerrada | 1. Mesa en estado cerrada<br>2. Jugador solicita | 409 "La mesa está cerrada". | `[ ]` | |
| TC-MESA-013d | Mesas (multi) | Aceptar sin cupo | 1. Cupo 0/2, solicitud pendiente<br>2. GM acepta | 409 y no consume plaza. | `[ ]` | |
| TC-MESA-013e | Mesas (multi) | No propietario acepta/rechaza | 1. Jugador intenta aceptar solicitud ajena | 403. | `[ ]` | |
| TC-MESA-013f | Mesas (multi) | Rate limit con varios usuarios | 1. 3 usuarios postulándose en secuencia rápida | Sin 429 indebidamente (cada uno su cupo por XFF). | `[ ]` | |
| TC-MULTI-001 | Concurrencia | Dos jugadores postulan simultáneamente | 1. Jugador A y B (browsers distintos) → "Solicitar unión" a mesa con 1 plaza libre | Ambas solicitudes pendientes; la 2ª no auto-acepta; cupo no se supera. | `[ ]` | |
| TC-MULTI-002 | Concurrencia | GM acepta mientras jugador mira `/mis-mesas` | 1. Jugador envía solicitud<br>2. GM acepta<br>3. Jugador refresca | La mesa aparece en `/mis-mesas` del jugador (no solo en `/mis-mesas-gm`). | `[ ]` | |
| TC-MULTI-003 | Concurrencia | Votación simultánea | 1. 2 jugadores votan a favor de la misma propuesta | Contador `2`; cada uno ve su propio `mi_voto`. | `[ ]` | |
| TC-MULTI-004 | Concurrencia | Builds públicos vs propios | 1. Usuario A publica; Usuario B ve en "Públicos"; A ve en "Mis builds" | Sin duplicados ni faltantes. | `[ ]` | |
| TC-MULTI-005 | Concurrencia | Notificaciones por usuario | 1. GM acepta solicitud del jugador A | Solo A recibe "Solicitud aceptada"; B no ve nada. | `[ ]` | |
| TC-MULTI-006 | Concurrencia | Rate limit por IP real | 1. Dos browsers desde IPs distintas | Cada uno su propio cupo (no se bloquean entre sí). | `[ ]` | |
| TC-MULTI-007 | Concurrencia | Aislamiento de identidad | 1. Token de A en browser B | No ve mesas/builds/notifs de A. | `[ ]` | |
| TC-MULTI-008 | Concurrencia | Wiki concurrente | 1. Dos jugadores editan/contribuyen a la misma página | Sin sobrescritura; contribuciones pendientes separadas. | `[ ]` | |
| TC-MULTI-009 | Concurrencia | Sesiones concurrentes | 1. Dos GMs crean sesiones en la misma mesa (no debería pasar) | Solo el GM propietario puede crear (403 para el otro). | `[ ]` | |
| TC-MULTI-010 | Concurrencia | Expulsión concurrente | 1. GM expulsa mientras jugador envía solicitud | Sin estado inconsistente; cupo correcto. | `[ ]` | |

### 2.19 Regresión de defectos corregidos

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-REG-001 | Regresión | D-01: detalle no se anula por getMiembros 403 | 1. Invitado → `/mesas/1` | Ficha visible; pestaña Personajes vacía (sin "Mesa no encontrada"). | `[ ]` | |
| TC-REG-002 | Regresión | D-02: shell carga parcial | 1. GM → `/mesas/1/gestion` con un endpoint secundario caído | Mesa visible con tabs; sección afectada degrada. | `[ ]` | |
| TC-REG-003 | Regresión | D-04: SesionesView sin TypeError con ≥2 sesiones | 1. `/mesas/1/gestion/sesiones` con 2+ sesiones | Renderiza sin crash; orden por fecha. | `[ ]` | |
| TC-REG-004 | Regresión | D-05: calendario con día+hora reales | 1. Proponer fecha con selector de día+hora | POST con ISO válido `YYYY-MM-DDTHH:mm:00`. | `[ ]` | |
| TC-REG-005 | Regresión | D-06: ambientación libre → tono | 1. Crear mesa con ambientación libre | Persiste en `tono`; no se envía `lugar`. | `[ ]` | |
| TC-REG-006 | Regresión | D-03: landing reconoce sesión | 1. Autenticado → `/` | Perfil + "Cerrar sesión" (no "Iniciar sesión" fijo). | `[ ]` | |
| TC-REG-007 | Regresión | D-07: sin pergamino global | 1. Navegar landing, mesas, gestión | Tema arcade oscuro (mint/rosa). Sin pergamino global. | `[ ]` | |
| TC-REG-008 | Regresión | D-09: estado canónico cerrada | 1. Mesa cerrada → detalle | Tag "Cerrada"; botón "Solicitar unión" deshabilitado. | `[ ]` | |
| TC-REG-009 | Regresión | D-10: cupo sin undefined/NaN | 1. Panel GM con cupo | "x/y" y vacantes numéricas (sin undefined/NaN). | `[ ]` | |
| TC-REG-010 | Regresión | D-11: rol real Master/Jugador | 1. Ver miembros en gestión | GM aparece como "Master", jugador como "Jugador". | `[ ]` | |
| TC-REG-011 | Regresión | D-12: GestionView GM real | 1. `/mesas/1/gestion` | GM real (no "Aldren Valeros"); ocupación real (no undefined). | `[ ]` | |
| TC-REG-012 | Regresión | D-13: nav sin enlaces muertos | 1. Navegar por nav/footer | Todas las rutas resuelven (no NotFound). | `[ ]` | |
| TC-REG-013 | Regresión | D-17: crear mesa devuelve gm_nombre | 1. Crear mesa → ver detalle | GM visible sin recargar. | `[ ]` | |
| TC-REG-014 | Regresión | D-14: mi_voto en fechas | 1. Jugador que ya votó → calendario | Su voto marcado (aria-pressed) con `mi_voto` real. | `[ ]` | |
| TC-REG-015 | Regresión | F09: consola admin real | 1. Login admin → `/admin` | Panel con event log, DLQ, emails reales. | `[ ]` | |
| TC-REG-016 | Regresión | Rate limit por XFF | 1. Dos browsers desde IPs distintas | Cada uno su propio cupo (no se bloquean entre sí). | `[ ]` | |
| TC-REG-017 | Regresión | Enlaces de notificaciones saneados | 1. Notificación vieja `/mesas/demo` | Redirige a `/mesas` (no "Mesa no encontrada"). | `[ ]` | |
| TC-REG-018 | Regresión | Shell único (sin doble render) | 1. `/mesas/1/gestion` | Un solo encabezado/tabs (no duplicado). | `[ ]` | |
| TC-REG-019 | Regresión | Diario con contrato real | 1. `/mesas/1/gestion/sesiones/:id/diario` | Formulario carga sin crash (sin `sesion.numero`). | `[ ]` | |
| TC-REG-020 | Regresión | Rate limit Retry-After | 1. Forzar 429 | Respuesta incluye header `Retry-After`. | `[ ]` | |

### 2.20 Flujos E2E completos

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-E2E-001 | E2E | Invitado → catálogo → detalle → login → solicitar unión | 1. Invitado → `/mesas` → abrir mesa → "Solicitar unión" (redirect login) → login → volver → solicitar | Solicitud enviada. Tag "Solicitud enviada". | `[ ]` | |
| TC-E2E-002 | E2E | Registro → crear mesa → gestión → calendario → proponer → confirmar → sesión → diario | 1. Registro → `/mesas/nueva` → crear → `/mis-mesas-gm` → gestión → calendario → proponer fecha+hora → confirmar → sesiones → diario → guardar | Flujo completo sin errores. Sesión creada. Diario guardado. | `[ ]` | |
| TC-E2E-003 | E2E | GM acepta solicitud → jugador ve membresía → expulsa | 1. Jugador solicita → GM acepta → jugador ve mesa en `/mis-mesas` → GM expulsa → jugador deja de verla | Membresía correcta en cada paso. | `[ ]` | |
| TC-E2E-004 | E2E | Votación de fechas | 1. GM propone → jugador vota favor → GM confirma | Fecha confirmada; sesión creada; calendario marca el día. | `[ ]` | |
| TC-E2E-005 | E2E | QR de asistencia | 1. GM genera QR → jugador valida (o GM valida) → single-use | Asistencia registrada; QR vencido/usado da 409. | `[ ]` | |
| TC-E2E-006 | E2E | Wiki colaborativa | 1. GM crea página → jugador contribuye → GM aprueba | Página publicada; contribución aprobada. | `[ ]` | |
| TC-E2E-007 | E2E | Builds | 1. Wizard → editar → vincular a mesa → publicar en feed → agregar a wiki | Build visible en mesa y feed. | `[ ]` | |
| TC-E2E-008 | E2E | Admin | 1. Login admin → event log → DLQ → emails | Todas las tablas cargan. Reintentar/descartar funcionan. | `[ ]` | |
| TC-E2E-009 | E2E | Logout y re-login | 1. Logout → login de nuevo | Sesión restaurada. Datos intactos. | `[ ]` | |
| TC-E2E-010 | E2E | Rate limit multi-usuario | 1. Dos usuarios navegando simultáneamente | Cada uno su cupo (sin 429 cruzado). | `[ ]` | |
| TC-E2E-011 | E2E | Crear mesa → aparece en `/mis-mesas-gm` | 1. Crear mesa → verificar listado | Mesa visible en "Donde dirigís hoy". | `[ ]` | |
| TC-E2E-012 | E2E | Build creado → aparece en "Mis builds" | 1. Crear build → ir a `/builds` pestaña "Mis builds" | Build visible (con nombre, no "Personaje sin nombre"). | `[ ]` | |
| TC-E2E-013 | E2E | Notificación de solicitud → click | 1. Jugador solicita → GM recibe notif → click | Navega a `/mesas/:id/gestion/jugadores` (no NotFound). | `[ ]` | |
| TC-E2E-014 | E2E | Notificación de diario publicado | 1. GM publica diario → jugador recibe notif | Click navega a `/mesas/:id`. | `[ ]` | |

### 2.21 Casos borde adicionales

| ID | Módulo | Escenario | Pasos | Resultado esperado | Estado | Comentarios |
|---|---|---|---|---|---|---|
| TC-EDGE-001 | Borde | Mesa con 0 jugadores (capacidad null) | 1. Mesa sin cupo definido | "∞" en cupo; sin NaN. | `[ ]` | |
| TC-EDGE-002 | Borde | Mesa sin horario | 1. Mesa con horario vacío | "A coordinar" (no "A coordinar" contaminando el campo editable). | `[ ]` | |
| TC-EDGE-003 | Borde | Build sin ficha | 1. Build borrador sin ficha | "La ficha OGL completa… aún no se ha publicado." | `[ ]` | |
| TC-EDGE-004 | Borde | Wiki sin páginas | 1. Mesa sin wiki | "El código no registra páginas…" | `[ ]` | |
| TC-EDGE-005 | Borde | Sesión sin fecha (no debería pasar) | 1. Verificar que no se crea sesión sin fecha | Backend rechaza. | `[ ]` | |
| TC-EDGE-006 | Borde | Notificación sin enlace | 1. Notificación con enlace null | Botón no se renderiza o lleva a `/notificaciones`. | `[ ]` | |
| TC-EDGE-007 | Borde | Usuario con nombre muy largo | 1. Nombre de 100 caracteres | Truncado en UI; sin overflow. | `[ ]` | |
| TC-EDGE-008 | Borde | Mesa con nombre con caracteres especiales | 1. Nombre con `<script>`, emojis, acentos | Sanitizado/aceptado sin XSS. | `[ ]` | |
| TC-EDGE-009 | Borde | Refresh durante carga | 1. F5 mientras carga | Sin crash; carga de nuevo. | `[ ]` | |
| TC-EDGE-010 | Borde | Token expirado en medio de navegación | 1. Token vence entre páginas | Redirect a login (idealmente con banner). | `[ ]` | |
| TC-EDGE-011 | Borde | Sesión con cupo 1 | 1. Mesa con cupo 1, 1 jugador | "1/1" y "Completa". Botón deshabilitado. | `[ ]` | |
| TC-EDGE-012 | Borde | Build con nivel 20 | 1. Build nivel 20 | Renderiza sin overflow. | `[ ]` | |
| TC-EDGE-013 | Borde | Notificación de evento global (usuario_id null) | 1. Evento de comunidad | Visible para todos los autenticados. | `[ ]` | |
| TC-EDGE-014 | Borde | Mesa eliminada mientras se ve | 1. GM elimina mesa en otra pestaña → refrescar | "Mesa no encontrada" (no crash). | `[ ]` | |
| TC-EDGE-015 | Borde | Propuesta de fecha en el pasado | 1. GM propone fecha pasada | 400 "La fecha propuesta no puede ser en el pasado." | `[ ]` | |

---

## 3. Formato de registro de fallos

Para cada `[!] Falló`, anotar en la columna **Comentarios / Logs de Fallo**:

```
Fallo: <descripción corta>
Pasos reproducidos: 1..N
Esperado: ...
Obtenido: ...
Consola: <error de JS o warning>
Network: <método> <url> → <status> · <cuerpo del error>
Dispositivo/navegador: Chrome 128 / Firefox 126 / Safari 17 / Android 14 / iOS 17
Screenshot: <nombre-archivo.png>
```

Con eso, pasame el checklist completado y te ayudo a corregir los defectos en el código (backend, frontend o datos) siguiendo TDD: RED con test que reproduce el fallo → GREEN con el fix mínimo → verificación.
