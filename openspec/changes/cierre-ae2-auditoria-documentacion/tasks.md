# Tasks

## 1. Preparar y documentar la auditoría

- [x] 1.1 Registrar la rama, commit base, fecha y alcance auditado en `docs/AUDITORIA_CIERRE_AE2.md`.
- [x] 1.2 Crear la matriz B01–B12 y F01–F09 con estado funcional, evidencia Git, estado OpenSpec, pruebas, evidencias y pendientes administrativos; verificar que las 21 tareas aparezcan individualmente.
- [x] 1.3 Documentar los hallazgos con severidad crítica/alta/media/baja, impacto, recomendación, archivos afectados y criterio de verificación.
- [x] 1.4 Separar explícitamente bloqueadores de cierre, pendientes administrativos y mejoras posteriores.

## 2. Ejecutar verificaciones reproducibles

- [x] 2.1 Levantar o documentar los prerrequisitos de PostgreSQL, Redis, RabbitMQ y MailHog requeridos por la suite.
- [ ] 2.2 Ejecutar `pytest tests -v` y registrar resultado, número de tests, fallos y requisitos no cumplidos.
- [x] 2.3 Ejecutar validaciones OpenSpec para el cambio y para los cambios AE2 relacionados; registrar errores o inconsistencias.
- [ ] 2.4 Verificar `/docs` y `/openapi.json` de mesas, builds, feed y notif; registrar rutas y errores de contrato.
- [ ] 2.5 Ejecutar `ruff check` si las dependencias están instaladas; registrar el resultado y no declarar lint verde si no pudo ejecutarse.
- [x] 2.6 Verificar `docker compose config` y la disponibilidad de healthchecks; documentar cualquier limitación del entorno.

## 3. Cerrar brechas de la auditoría

- [ ] 3.1 Crear issues de remediación para los hallazgos críticos y altos, incluyendo DLQ sin autenticación, enumeración de correo, secretos por defecto, aplicación raíz rota, SQL dinámico y falta de CI/CD.
- [ ] 3.2 Crear issues separadas para brechas de testing: tests unitarios, cobertura de builds/feed/notif, E2E frontend y pruebas de carga.
- [ ] 3.3 Asignar prioridad, responsable, criterio de aceptación y evidencia requerida a cada issue de remediación.
- [x] 3.4 Decidir y documentar el tratamiento de los valores por defecto de secretos para desarrollo versus producción.

## 4. Cerrar entrega y sincronizar herramientas

- [ ] 4.1 Actualizar los checklists de OpenSpec de B01–B12 y F01–F09 para reflejar implementación, verificación y cierre real.
- [ ] 4.2 Archivar los cambios OpenSpec que estén completos y mantener abiertos los que tengan tareas técnicas reales.
- [ ] 4.3 Verificar o crear issues GitHub #20–#34, asociando cada issue con su commit, evidencia y tarea OpenSpec.
- [ ] 4.4 Agregar las issues al tablero Kanban correcto y asignar estados `Backlog`, `In Progress` o `Done` según la evidencia.
- [ ] 4.5 Verificar tags `2.0.0` y `2.1.0` y documentar el commit al que apunta cada tag.
- [ ] 4.6 Preparar el PR final con checklist de pruebas, resumen de auditoría, riesgos pendientes y referencias a issues.
- [x] 4.7 Actualizar `AE2/README.md` para enlazar `docs/AUDITORIA_CIERRE_AE2.md` y diferenciar el estado funcional del estado de cierre.
- [ ] 4.8 Realizar una revisión final de consistencia: matriz, issues, OpenSpec, Kanban, tags, PR y evidencias deben apuntar al mismo estado.
