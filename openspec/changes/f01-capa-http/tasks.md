## 1. Implementación

- [x] 1.1 `src/config/api.js`: orígenes por servicio (8001–8004, env `VITE_*_API`) + `apiUrl`
- [x] 1.2 `src/api/http.js`: `api()` con timeout 8 s (AbortController)
- [x] 1.3 Headers: `Authorization` si hay sesión, `X-Correlation-Id` por request, `Idempotency-Key` si hay cuerpo
- [x] 1.4 `401` → `clearSession()` + redirect `/login?redirect=...` + `ApiError(401)`
- [x] 1.5 Errores `{error:{codigo,mensaje}}` → `ApiError{codigo,mensaje,detalles}` (fallback `HTTP <status>`)
- [x] 1.6 `src/api/endpoints.js`: `authApi`, `mesasApi`, `notifApi`
- [x] 1.7 `useAuth.js`: exports aditivos `currentAccessToken()` y `clearSession()`
- [x] 1.8 Build: `npm run build` compila sin errores

## 2. Verificación

- [x] 2.1 `openspec validate f01-capa-http`

## 3. Cierre de la tarea

- [ ] 3.1 Rama `f/F01_capa_http`, commit, merge y archivar
- [ ] 3.2 Cerrar issue GitHub #26