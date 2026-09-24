## 1. Implementación

- [x] 1.1 `endpoints.js`: `sesionesApi.qr` y `sesionesApi.validarQr`
- [x] 1.2 `SesionQrView.vue`: generación PNG + countdown + regenerar, y panel GM de validación
- [x] 1.3 Router: ruta `/mesas/:id/sesiones/:sesionId/qr`
- [x] 1.4 `SesionesView.vue`: enlace "Asistencia (QR)"
- [x] 1.5 `npm run build` compila sin errores

## 2. Verificación

- [x] 2.1 Jugador genera QR → `png_base64`, `qr_data`, `expira_en_seg=600`
- [x] 2.2 Payload del QR decodificado solo contiene `{sesion, u, exp}` (sin email/nombre)
- [x] 2.3 GM valida → 1ª vez 200 `asistencia: registrada`
- [x] 2.4 Mismo QR de nuevo → 409 "QR vencido o ya utilizado"
- [x] 2.5 `openspec validate f06-qr-asistencia`

## 3. Cierre de la tarea

- [ ] 3.1 Rama `f/F06_qr_asistencia`, commit, merge y archivar
- [ ] 3.2 Cerrar issue GitHub #31