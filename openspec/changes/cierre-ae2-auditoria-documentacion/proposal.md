# Proposal

## Why

La implementación funcional de AE2 largely existe, pero el estado real está fragmentado entre commits, checklists de OpenSpec, issues previstas y documentación de auditoría. Falta un documento único, trazable y accionable que distinga qué está implementado, qué queda pendiente, qué riesgos bloquean el cierre y cómo verificar cada punto antes de declarar la entrega finalizada.

## What Changes

- Crear un documento de resumen ejecutivo de auditoría y cierre de AE2.
- Consolidar el estado real de B01–B12 y F01–F09 contrastando código, commits, merges, OpenSpec y evidencias.
- Documentar hallazgos priorizados con severidad, evidencia, impacto y recomendación.
- Documentar brechas de testing, seguridad, operación, CI/CD y documentación.
- Definir el procedimiento de cierre: actualización de checklists, archivado de OpenSpec, cierre de issues, tablero Kanban, tags y PR final.
- Incorporar criterios de aceptación y comandos de verificación para que el documento pueda usarse como plan de ejecución.

## Capabilities

### New Capabilities

- `auditoria-cierre-ae2`: Resumen auditable del estado de AE2, brechas detectadas, plan de remediación y criterios de cierre.

### Modified Capabilities

- Ninguna. El cambio planifica documentación y gestión de entrega; no modifica todavía los requisitos funcionales del sistema.

## Impact

- Documentación nueva del repositorio y, cuando se implemente, un índice de evidencias.
- OpenSpec: cambios y tareas existentes que deben actualizarse o archivarse.
- GitHub: issues, tablero de proyecto, etiquetas, estados y PR final.
- Repositorio: checks de pytest, OpenSpec, OpenAPI, lint y Docker.
- No se modifica código de aplicación durante la creación de los artefactos de planificación.
