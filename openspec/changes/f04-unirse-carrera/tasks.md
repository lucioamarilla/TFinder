## 1. Implementación

- [x] 1.1 `endpoints.js`: `solicitarUnion(id, cuerpo, key)` → `/solicitudes` con `Idempotency-Key`
- [x] 1.2 `useSolicitud.js`: key persistida por `(mesa, usuario)` + estados `inactivo/enviando/solicitada/agotada/error`
- [x] 1.3 `MesaDetailView`: botón por estado con `disabled`/`aria-busy`, alerta "última vacante en disputa", aviso de cupo agotado y toasts
- [x] 1.4 `npm run build` compila sin errores

## 2. Verificación

- [x] 2.1 Doble barrera real: PA `201`, PB `409`, replay de PA con misma key `201` y ocupación sin duplicar (1/1)
- [x] 2.2 `openspec validate f04-unirse-carrera`

## 3. Cierre de la tarea

- [ ] 3.1 Rama `f/F04_unirse_carrera`, commit, merge y archivar
- [ ] 3.2 Cerrar issue GitHub #29