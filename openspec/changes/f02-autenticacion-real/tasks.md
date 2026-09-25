## 1. Implementación

- [x] 1.1 `useAuth.js` a tokens: login (auth+me), logout (revoca), `clearSession`, `currentAccessToken`, `currentRole` con mapeo de roles backend→nav
- [x] 1.2 `LoginView`: login real con `ApiError`, redirect query/admin, sin selector fake
- [x] 1.3 `RegistroView`: register real + login automático + error 400 de duplicado
- [x] 1.4 `RecuperarView`: POST a notif `/api/v1/auth/recuperar` (202 → revisá tu casilla; timeout → servicio no disponible)
- [x] 1.5 notif-api: ruta `POST /api/v1/auth/recuperar` (202 genérico + email transaccional) e include en main
- [x] 1.6 Rebuild de imagen `notif-api` y verificación del endpoint (202 + correo en MailHog)
- [x] 1.7 `npm run build` compila sin errores

## 2. Verificación

- [x] 2.1 Flujo real: register 201 → me 200 → logout 200 → me con token revocado 401
- [x] 2.2 `openspec validate f02-autenticacion-real`

## 3. Cierre de la tarea

- [ ] 3.1 Rama `f/F02_autenticacion_real`, commit, merge y archivar
- [ ] 3.2 Cerrar issue GitHub #27