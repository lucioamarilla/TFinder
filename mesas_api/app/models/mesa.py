from mesas_api.app.db import get_connection
from mesas_api.app.schemas import EDITABLE_FIELDS, MesaCreate, MesaUpdate


def _normalizar_create(data):
    if isinstance(data, MesaCreate):
        return data
    return MesaCreate(**data)


def listar_mesas():
    with get_connection() as conn:
        filas = conn.execute("SELECT * FROM mesas ORDER BY id").fetchall()
        return [dict(fila) for fila in filas]


def obtener_mesa_por_id(mesa_id):
    with get_connection() as conn:
        fila = conn.execute("SELECT * FROM mesas WHERE id = %s", (mesa_id,)).fetchone()
        return dict(fila) if fila else None


def crear_mesa(data):
    datos = _normalizar_create(data).model_dump()
    columnas = ", ".join(datos.keys())
    placeholders = ", ".join(["%s"] * len(datos))
    with get_connection() as conn:
        cursor = conn.execute(
            f"INSERT INTO mesas ({columnas}) VALUES ({placeholders}) RETURNING id",
            tuple(datos.values()),
        )
        mesa_id = cursor.fetchone()["id"]
        fila = conn.execute("SELECT * FROM mesas WHERE id = %s", (mesa_id,)).fetchone()
        return dict(fila)


def actualizar_mesa(mesa_id, data):
    cambios = data.model_dump(exclude_unset=True)
    cambios = {k: v for k, v in cambios.items() if k in EDITABLE_FIELDS}
    with get_connection() as conn:
        if not cambios:
            fila = conn.execute(
                "SELECT * FROM mesas WHERE id = %s", (mesa_id,)
            ).fetchone()
            return dict(fila) if fila else None
        asignaciones = ", ".join(f"{k} = %s" for k in cambios)
        cursor = conn.execute(
            f"UPDATE mesas SET {asignaciones} WHERE id = %s",
            (*cambios.values(), mesa_id),
        )
        if cursor.rowcount == 0:
            return None
        fila = conn.execute("SELECT * FROM mesas WHERE id = %s", (mesa_id,)).fetchone()
        return dict(fila)


def eliminar_mesa(mesa_id):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM mesas WHERE id = %s", (mesa_id,))
        return cursor.rowcount