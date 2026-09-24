## 1. Implementación

- [x] 1.1 Backend: `PATCH /notificaciones/{id}/leida` + `creado_en` en `NotificacionOut`
- [x] 1.2 `endpoints.js`: reutiliza `notifApi` existente (notificaciones + marcarLeida)
- [x] 1.3 `services/notificaciones.js`: servicio real con mapeo de enlace y fecha
- [x] 1.4 `useNotifications.js`: polling 5 s, estado compartido, `desconectado`
- [x] 1.5 `AppHeader.vue`: badge real + offline
- [x] 1.6 `NotificacionesView.vue`: lista compartida, recargar, offline, navegación por enlace
- [x] 1.7 `npm run build` compila sin errores

## 2. Verificación

- [x] 2.1 Solicitud de unión a mesa con vacante → 201 → notificación "Solicitud aceptada" persistida (total 38→39)
- [x] 2.2 PATCH leída → `leida:true` y no_leidas decrementa
- [x] 2.3 `docker stop` notif-api → sin respuesta (HTTP 000) → la UI sigue y marca offline
- [x] 2.4 `openspec validate f08-notif-pollo`

## 3. Cierre de la tarea

- [ ] 3.1 Rama `f/F08_notif_polling`, commit, merge y archivar
- [ ] 3.2 Cerrar issue GitHub #33