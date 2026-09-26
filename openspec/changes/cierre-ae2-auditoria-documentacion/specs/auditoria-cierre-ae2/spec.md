# Spec Delta

## Purpose

Permite cerrar AE2 con una auditoría reproducible que separe funcionalidad implementada, pendientes administrativos, riesgos técnicos y verificaciones ejecutables, evitando declarar como terminado lo que solo está parcialmente integrado.

## ADDED Requirements

### Requirement: Informe consolidado de auditoría
El repositorio SHALL contener un documento de auditoría de AE2 que identifique el estado de B01–B12 y F01–F09 usando evidencia observable del proyecto, incluyendo código, historial Git, OpenSpec, tests y evidencias existentes.

#### Scenario: Consultar el estado de una tarea
- **WHEN** un responsable consulta el documento de auditoría para una tarea B01–B12 o F01–F09
- **THEN** el documento muestra su estado funcional, evidencia, pendientes administrativos y cualquier bloqueo identificado

### Requirement: Hallazgos priorizados y accionables
El documento SHALL clasificar los hallazgos por severidad crítica, alta, media o baja y SHALL indicar para cada hallazgo su impacto, recomendación y archivos afectados.

#### Scenario: Revisar un hallazgo crítico
- **WHEN** se revisa un hallazgo marcado como crítico
- **THEN** el documento identifica el riesgo, su impacto, la acción recomendada y la verificación necesaria para resolverlo

### Requirement: Matriz de trazabilidad
El documento SHALL relacionar cada tarea de AE2 con su estado en OpenSpec, commit o merge relevante, cobertura de pruebas y evidencia asociada.

#### Scenario: Verificar una funcionalidad entregada
- **WHEN** se verifica B01–B12 o F01–F09 contra la matriz
- **THEN** el lector puede distinguir entre implementación funcional completada, tarea administrativa pendiente y funcionalidad no verificada

### Requirement: Plan de cierre reproducible
El documento SHALL definir los pasos necesarios para actualizar checklists, archivar cambios OpenSpec, cerrar issues, actualizar el tablero Kanban, crear tags y preparar el PR final.

#### Scenario: Ejecutar el cierre documental
- **WHEN** una persona responsable sigue el plan de cierre
- **THEN** encuentra el orden de las acciones, sus comandos o criterios y la evidencia requerida antes de cerrar cada tarea

### Requirement: Verificación reproducible
El documento SHALL incluir comandos de verificación para tests backend, validación OpenSpec, OpenAPI de los cuatro servicios, lint cuando exista y estado de Docker Compose.

#### Scenario: Evaluar el estado técnico antes del cierre
- **WHEN** se ejecuta el checklist de verificación
- **THEN** cada verificación reporta el resultado esperado, los prerrequisitos de infraestructura y el tratamiento de un resultado fallido

### Requirement: Separación entre auditoría y remediación
El documento SHALL distinguir entre problemas que impiden cerrar AE2 y mejoras posteriores, y SHALL evitar presentar comoClosed cualquier tarea cuya funcionalidad no esté verificada.

#### Scenario: Tratar un bloqueo de seguridad
- **WHEN** un hallazgo crítico impide declarar la entrega como cerrada
- **THEN** el documento lo clasifica como bloqueo de cierre y define una tarea de remediación o issue separada

## Non-goals

- No modificar el comportamiento de los servicios como parte de este cambio documental.
- No reemplazar las especificaciones funcionales existentes de B01–B12 o F01–F09.
- No cerrar issues remotas ni ejecutar merges automáticamente como parte de la generación del informe.
