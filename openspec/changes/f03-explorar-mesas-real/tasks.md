## 1. Implementación

- [x] 1.1 `src/services/mesas.js` reimplementado sobre `mesasApi` (misma firma + normalización a shape interno + `ultimaMedicion()`)
- [x] 1.2 `src/api/endpoints.js`: `actualizar`/`eliminar` y `solicitarUnion` → ruta real `/mesas/{id}/solicitar`
- [x] 1.3 `MesasListView`: chip "caché ~X ms" + botón "Refrescar" + error con Reintentar intacto
- [x] 1.4 `MesaDetailView`: campos reales del API y botón "Reintentar" en error
- [x] 1.5 `npm run build` compila sin errores

## 2. Verificación

- [x] 2.1 API real: 1ª carga (cold) y 2ª carga (caché) responden 200; tiempos observables
- [x] 2.2 `openspec validate f03-explorar-mesas-real`

## 3. Cierre de la tarea

- [ ] 3.1 Rama `f/F03_explorar_mesas_real`, commit, merge y archivar
- [ ] 3.2 Cerrar issue GitHub #28