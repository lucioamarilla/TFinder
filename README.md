# TFinder — Módulo de Gestión de Mesas (AE1)

**TFinder** es una API REST para gestionar la entidad **Mesa**, basada en el juego de rol **Pathfinder 1.ª edición**. El objetivo es realizar un **CRUD completo** (crear, listar, obtener, actualizar y eliminar) de mesas de juego, cumpliendo con las **consignas del AE1** de la materia Paradigmas III. La aplicación está construida con FastAPI, persiste en SQLite y maneja de forma centralizada los errores con un formato de respuesta uniforme.

## Integrantes
- Amarilla Lucio
- Czajkowski Leonardo

## Stack Tecnológico
- Lenguaje: Python 3.11+
- Framework: FastAPI
- Persistencia: SQLite
- Servidor ASGI: Uvicorn

## Requisitos previos
- Python 3.11 o superior instalado (`python --version`).
- `pip` disponible (incluido con Python).

## Estructura del proyecto
```bash
TFinder/
├── .env                        # (NO se sube, va en .gitignore)
├── .env.example                # sí se sube, con claves sin valores sensibles
├── .gitignore
├── requirements.txt
├── README.md
├── REPORTE_PRUEBAS.md          # reporte de pruebas funcionales de los endpoints
├── schema.sql                  # DDL de la tabla mesas
├── main.py                     # punto de entrada, instancia FastAPI, arranca Uvicorn
└── app/
    ├── __init__.py
    ├── db.py                   # conexión SQLite + init_db() + migraciones
    ├── routes/
    │   ├── __init__.py
    │   └── mesas_routes.py     # define los endpoints /api/v1/mesas
    ├── controllers/
    │   ├── __init__.py
    │   └── mesas_controller.py # lógica intermedia entre rutas y modelo
    ├── models/
    │   ├── __init__.py
    │   └── mesas_model.py      # esquemas Pydantic (MesaCreate, MesaUpdate, MesaOut) + acceso a datos
    └── middleware/
        ├── __init__.py
        └── error_handler.py    # manejador centralizado de excepciones (400/404/500)
```

## Instalación

```bash
git clone https://github.com/lucioamarilla/TFinder
cd TFinder
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> **Nota**: el comando usa `python3`. En sistemas Ubuntu/Debian recientes `python` no existe por defecto; será `python3`. En otras distribuciones o si tenés un alias `python` (que apunte a Python 3), también podés usar `python -m venv venv`.

## Configuración

Copiar `.env.example` a `.env` y completar los valores:

```bash
cp .env.example .env
```

Variables:

| Variable | Descripción | Ejemplo |
|---|---|---|
| PORT | Puerto del servidor | 8000 |
| DATABASE_URL | Ruta al archivo SQLite | ./tfinder.db |

> **Nota**: si las variables se dejan vacías, el servidor usa sus valores por defecto (`PORT=8000` y `SQLite` en `./tfinder.db`).

## Ejecución

```bash
uvicorn main:app --reload --port 8000
```

- Al arrancar, `init_db()` crea automáticamente el archivo `tfinder.db` y la tabla `mesas` (si no existen) y aplica las migraciones necesarias.
- Documentación interactiva (Swagger): http://localhost:8000/docs
- Esquema OpenAPI: http://localhost:8000/openapi.json

## Modelo de datos — entidad Mesa

| Campo | Tipo | Obligatorio | Validación |
|---|---|---|---|
| nombre | TEXT | Sí | mínimo 1 carácter |
| sistema | TEXT | Sí | mínimo 1 carácter |
| descripcion | TEXT | No | — |
| tono | TEXT | No | — |
| horario | TEXT | No | — |
| estado | TEXT | No | `abierta` o `cerrada` (default: `abierta`) |
| nivel_inicial | INTEGER | No | >= 0, tipo estricto |
| jugadores_max | INTEGER | No | > 0, tipo estricto |
| fecha_creacion | DATETIME | No | se asigna automáticamente |

> **Campos de tipo estricto**: `nivel_inicial` y `jugadores_max` deben enviarse como números JSON reales. Si se envían como string (ej. `"5"`), la API los rechaza con `400`.

## Endpoints

Todas las rutas tienen el prefijo `/api/v1`. Los errores siguen el formato unificado descrito en [Formato de errores](#formato-de-errores).

### GET /api/v1/mesas
Lista todas las mesas.
- Respuesta: `200 OK` + array JSON

```bash
curl http://localhost:8000/api/v1/mesas
```

**Respuesta — `200 OK`:**
```json
[
  {
    "id": 1,
    "nombre": "Mesa Alpha",
    "sistema": "Pathfinder",
    "descripcion": null,
    "tono": null,
    "horario": null,
    "estado": "abierta",
    "nivel_inicial": null,
    "jugadores_max": 5,
    "fecha_creacion": "2026-08-28 19:28:30"
  }
]
```

### GET /api/v1/mesas/{id}
Obtiene una mesa por ID.
- `200 OK` + objeto Mesa si existe
- `404 Not Found` + `{"error": {"codigo": 404, "mensaje": "..."}}` si no existe

```bash
curl http://localhost:8000/api/v1/mesas/1
```

**Respuesta — `200 OK`:**
```json
{
  "id": 1,
  "nombre": "Mesa Alpha",
  "sistema": "Pathfinder",
  "descripcion": null,
  "tono": null,
  "horario": null,
  "estado": "abierta",
  "nivel_inicial": null,
  "jugadores_max": 5,
  "fecha_creacion": "2026-08-28 19:28:30"
}
```

**Respuesta — `404 Not Found` (id inexistente):**
```json
{"error": {"codigo": 404, "mensaje": "Mesa 9999 no encontrada"}}
```

### POST /api/v1/mesas
Crea una mesa. Body: `{"nombre": "...", "sistema": "...", ...}`
- `201 Created` + objeto creado (campos obligatorios: `nombre`, `sistema`)
- `400 Bad Request` si faltan campos obligatorios o hay datos inválidos

```bash
curl -X POST http://localhost:8000/api/v1/mesas \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Mesa Alpha", "sistema": "Pathfinder", "jugadores_max": 5}'
```

**Respuesta — `201 Created`:**
```json
{
  "id": 1,
  "nombre": "Mesa Alpha",
  "sistema": "Pathfinder",
  "descripcion": null,
  "tono": null,
  "horario": null,
  "estado": "abierta",
  "nivel_inicial": null,
  "jugadores_max": 5,
  "fecha_creacion": "2026-08-28 19:28:30"
}
```

**Respuesta — `400 Bad Request` (faltan campos obligatorios):**
```json
{"error": {"codigo": 400, "mensaje": "body.nombre: Field required; body.sistema: Field required"}}
```

### PUT /api/v1/mesas/{id}
Actualiza una mesa existente (update parcial: solo cambia los campos enviados).
- `200 OK` + objeto actualizado
- `404 Not Found` si no existe
- `400 Bad Request` si hay datos inválidos

```bash
curl -X PUT http://localhost:8000/api/v1/mesas/1 \
  -H "Content-Type: application/json" \
  -d '{"estado": "cerrada", "jugadores_max": 4}'
```

**Respuesta — `200 OK`:**
```json
{
  "id": 1,
  "nombre": "Mesa Alpha",
  "sistema": "Pathfinder",
  "descripcion": null,
  "tono": null,
  "horario": null,
  "estado": "cerrada",
  "nivel_inicial": null,
  "jugadores_max": 4,
  "fecha_creacion": "2026-08-28 19:28:30"
}
```

**Respuesta — `404 Not Found` (id inexistente):**
```json
{"error": {"codigo": 404, "mensaje": "Mesa 9999 no encontrada"}}
```

### DELETE /api/v1/mesas/{id}
Elimina una mesa existente.
- `204 No Content` si se elimina (sin body)
- `404 Not Found` si no existe

```bash
curl -X DELETE http://localhost:8000/api/v1/mesas/1
```

**Respuesta — `204 No Content`** (sin cuerpo en la respuesta).

**Respuesta — `404 Not Found` (id inexistente):**
```json
{"error": {"codigo": 404, "mensaje": "Mesa 9999 no encontrada"}}
```

## Formato de errores

Todos los errores de la API (400, 404, 500) devuelven una respuesta con la misma estructura:

```json
{"error": {"codigo": 404, "mensaje": "Mesa no encontrada"}}
```

| Código | Significado |
|---|---|
| 400 | Datos de entrada inválidos (validación) |
| 404 | Recurso no encontrado |
| 500 | Error interno del servidor |
