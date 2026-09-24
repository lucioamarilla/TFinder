## 1. Implementación

- [x] 1.1 `endpoints.js`: `matchmakingApi` con `abrir(mmId)` y `estado(mmId)`
- [x] 1.2 `useLlamado.js`: polling de 2 s del `ttl_restante` real de Redis
- [x] 1.3 `LlamadoCard.vue`: chip de TTL, botón GM "Abrir llamado" y jugador "Anotarse al llamado"
- [x] 1.4 `MatchmakingView.vue`: catálogo real de mesas con vacante + `LlamadoCard`
- [x] 1.5 `npm run build` compila sin errores

## 2. Verificación

- [x] 2.1 GM abre el llamado → `estado: abierto`, `ttl_restante: 120` y `redis-cli TTL llamado:<id>` = 120
- [x] 2.2 El TTL desciende en vivo (120 → 108 s) reflejando el valor de Redis
- [x] 2.3 Dos jugadores anotados sobre mesa de 2 plazas → 201 y 201; tercero → 409; ocupación final 2/2
- [x] 2.4 `openspec validate f05-llamado-ttl`

## 3. Cierre de la tarea

- [ ] 3.1 Rama `f/F05_llamado_ttl`, commit, merge y archivar
- [ ] 3.2 Cerrar issue GitHub #30