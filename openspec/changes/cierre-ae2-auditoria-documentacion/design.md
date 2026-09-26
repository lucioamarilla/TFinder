# Design

## Context

El repositorio contiene una implementación AE2 distribuida entre cuatro servicios FastAPI, un frontend Vue, PostgreSQL, Redis, RabbitMQ, MailHog, tests pytest, evidencias y cambios OpenSpec. El historial Git muestra merges funcionales de B01–B12 y F01–F09, pero varios `tasks.md` aún tienen pendientes de cierre, mientras que la auditoría detectó bloqueos de seguridad, una aplicación raíz rota, brechas de cobertura y ausencia de CI/CD.

El nuevo documento debe ser una fuente de verdad operativa para separar:

- funcionalidad implementada y demostrada;
- funcionalidad implementada pero pendiente de verificación completa;
- tareas administrativas de cierre;
- riesgos que impiden declarar la entrega como cerrada;
- mejoras posteriores.

## Goals / Non-Goals

**Goals:**

- Crear un informe auditable y actualizado mediante evidencia del repositorio.
- Mantener trazabilidad entre tareas, OpenSpec, Git, tests y evidencias.
- Definir un plan de cierre seguro y reproducible.
- Hacer explícitos los límites entre documentación, remediación de código y gestión remota.

**Non-Goals:**

- Corregir código, seguridad, infraestructura o tests dentro de este cambio documental.
- Cambiar contratos de APIs o requisitos funcionales existentes.
- Ejecutar automáticamente comandos que modifiquen GitHub, ramas, issues, tags o merges.

## Decisions

### D1 — El informe será un documento independiente de OpenSpec

Se creará `docs/AUDITORIA_CIERRE_AE2.md` como resumen legible para responsables y evaluación. OpenSpec conservará el contrato formal de esta capacidad y los cambios B01–B12/F01–F09 seguirán siendo la fuente de detalle funcional.

**Alternativa considerada:** modificar únicamente `AE2/README.md`. Se descarta porque el README actual describe la entrega y el运行方式, pero no separa hallazgos, bloqueos, brechas y tareas administrativas con suficiente detalle.

### D2 — Estado basado en evidencia, no solo en checkboxes

Cada tarea tendrá cuatro dimensiones: implementación, verificación, cierre administrativo y riesgo residual. El informe distinguirá explícitamente entre “funcionalidad hecha” y “tarea cerrada”, porque los checkmarks y el estado de Git/OpenSpec pueden estar desactualizados.

**Alternativa considerada:** usar exclusivamente el porcentaje de `openspec list`. Se descarta porque el porcentaje incluye tareas de cierre y no mide cobertura de seguridad, CI/CD o calidad.

### D3 — Hallazgos separados de remediación

El informe.catalogará hallazgos con severidad, impacto, recomendación, archivos afectados y criterio de verificación. Cada bloqueo de cierre será convertido en una tarea accionable o issue de remediación, pero no se implementará dentro de este cambio.

**Alternativa considerada:** arreglar todos los hallazgos durante la redacción. Se descarta porque mezclaría documentación y cambios de comportamiento, dificultando revisar y revertir la entrega.

### D4 — Verificación con prerrequisitos explícitos

Los comandos de pytest, OpenSpec, OpenAPI, Docker y lint se documentarán con sus dependencias. La ausencia de una variable, servicio o archivo se marcará como “no verificable” y no como aprobado.

### D5 — Cierre remotoRequires supervision humana

El documento describirá cómo actualizar issues, Kanban, OpenSpec, tags y PR, pero no ejecutará acciones remotas. Cada acción remota tendrá un criterio de aceptación y una evidencia que la persona responsable debe revisar.

## Risks / Trade-offs

- **El historial Git puede contener merges y tareasOpenSpec sin cerrar** → mostrar ambos estados y una matriz de discrepancias.
- **La suite depende de infraestructura local** → indicar comandos de arranque, variables requeridas y resultado esperado de cada test.
- **La auditoría puede quedar desactualizada** → fechar el informe, indicar commit/base auditado y definir un procedimiento de actualización.
- **Los hallazgos críticos pueden impedir el cierre** → clasificarlos como bloqueantes y no declarar AE2 cerrado hasta verificarlos.
- **El conteo de tareas puede ser ambiguo** → documentar explícitamente que B01–B12 y F01–F09 suman 21 tareas funcionales y separar cualquier archivo auxiliar.

## Migration Plan

1. Crear el informe con el estado observado en la rama auditada.
2. Contrastar la matriz con OpenSpec, Git, tests, evidencias y documentación existente.
3. Ejecutar verificaciones reproducibles y registrar resultados, sin corregir código en este paso.
4. Separar bloqueadores de AE2 de mejoras posteriores.
5. Revisar el informe con el equipo.
6. Crear issues y tareas de remediación o cierre según el plan aprobado.
7. Actualizar `AE2/README.md` y OpenSpec para enlazar el informe.
8. Archivar cambios OpenSpec, cerrar issues, actualizar Kanban, crear tags y preparar PR final.
9. Si una remediación cambia comportamiento, registrar como cambio OpenSpec separado antes de implementarla.

## Open Questions

- La rama y commit que se utilizarán como referencia final deben confirmarse antes de cerrar el PR.
- El alcance de los issues existentes (#20–#34) debe confirmarse contra GitHub antes de ejecutar cierres o merges.
