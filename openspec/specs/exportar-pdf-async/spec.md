# Purpose

Convertir el botón "Exportar PDF" en un flujo asíncrono real: la petición a `builds-api` responde 202 con un `documento_id`, la UI muestra "Generando… (en cola)" sin bloquear, y al consultar `notif-api` el documento pasa a "listo para descargar" (PDF real `application/pdf`). Los fallos se muestran como "Falló la generación: <motivo>".

## Requirements

### Requirement: Flujo asíncrono de exportación PDF
El botón "Exportar PDF" DEBE transitar por `inactivo → enviando → en_cola → listo` (o `error`). Al hacer clic, DEBE enviar el POST a `builds-api` y, si responde 202, guardar el `documento_id` y pasar a "en cola" consultando periódicamente `notif-api`. Al recibir 200 DEBE ofrecer "Descargar PDF" abriendo el endpoint real que sirve `application/pdf`. El estado "en cola" NO DEBE bloquear el resto de la pantalla.

#### Scenario: Del 202 al PDF listo
- **GIVEN** el usuario en la ficha de un build
- **WHEN** hace clic en "Exportar PDF"
- **THEN** recibe 202 con `documento_id` y ve "Generando… (en cola)"
- **AND** cuando `notif-api` responde 200, el botón pasa a "Descargar PDF" y descarga un PDF real (`application/pdf`)

### Requirement: Errores visibles de la generación
Si `notif-api` devuelve un error distinto de 404 (documento en proceso), la UI DEBE salir a `error` y mostrar "Falló la generación: <motivo>", permitiendo reintentar.

#### Scenario: Fallo en el estado
- **GIVEN** un `documento_id` que `notif-api` no puede resolver fuera de "en proceso"
- **WHEN** el polling consulta el estado
- **THEN** el botón muestra "Falló la generación: <motivo>" y "Reintentar"