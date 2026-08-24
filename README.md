# TFinder — Módulo de Gestión de Mesas (AE1)

Breve descripción: 2-3 líneas explicando qué es TFinder y qué resuelve este 
incremento (CRUD de la entidad Mesa).

## Integrantes
- Amarilla Lucio
- Czajkowski Leonardo

## Stack Tecnológico
- Lenguaje: Python 3.11+
- Framework: FastAPI
- Persistencia: SQLite
- Servidor ASGI: Uvicorn

## Estructura del proyecto
(pegar el árbol de carpetas de arriba, con una línea explicando qué hace cada capa)

## Instalación

\`\`\`bash
git clone https://github.com/usuario/tfinder-mesas-ae1.git
cd tfinder-mesas-ae1
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

## Configuración

Copiar `.env.example` a `.env` y completar los valores:

\`\`\`bash
cp .env.example .env
\`\`\`

Variables:
| Variable | Descripción | Ejemplo |
|---|---|---|
| PORT | Puerto del servidor | 8000 |
| ENV_MODE | Modo de ejecución | development |
| DATABASE_URL | Ruta al archivo SQLite | ./tfinder.db |

## Ejecución

\`\`\`bash
uvicorn main:app --reload --port 8000
\`\`\`

Documentación interactiva (Swagger): http://localhost:8000/docs

## Endpoints

### GET /api/v1/mesas
Lista todas las mesas.
- Respuesta: `200 OK` + array JSON

### GET /api/v1/mesas/{id}
Obtiene una mesa por ID.
- `200 OK` + objeto Mesa si existe
- `404 Not Found` + `{"error": {"codigo": 404, "mensaje": "..."}}` si no existe

### POST /api/v1/mesas
Crea una mesa. Body: `{"nombre": "...", "sistema": "...", ...}`
- `201 Created` + objeto creado (campos obligatorios: nombre, sistema)
- `400 Bad Request` si faltan campos obligatorios

### PUT /api/v1/mesas/{id}
Actualiza una mesa existente.
- `200 OK` + objeto actualizado
- `404 Not Found` si no existe

### DELETE /api/v1/mesas/{id}
Elimina una mesa existente.
- `204 No Content` si se elimina
- `404 Not Found` si no existe

## Estructura de errores

\`\`\`json
{"error": {"codigo": 404, "mensaje": "Mesa no encontrada"}}
\`\`\`

## Testing manual
Se probó cada endpoint con Postman (ver capturas en el informe técnico, Anexo).