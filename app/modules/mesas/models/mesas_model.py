from typing import Optional

from app.core.db import get_db_connection

from app.modules.mesas.schemas.mesas_schema import (
    EDITABLE_FIELDS,
    MesaCreate,
    MesaUpdate,
)


def _normalizar_create(data):
    if isinstance(data, MesaCreate):
        return data
    return MesaCreate(**data)


def _normalizar_update(data):
    if isinstance(data, MesaUpdate):
        return data
    return MesaUpdate(**data)


def _fila_a_dict(fila):
    if fila is None:
        return None
    return dict(fila)


def listar_mesas():
    conn = get_db_connection()
    try:
        filas = conn.execute("SELECT * FROM mesas ORDER BY id").fetchall()
        return [_fila_a_dict(f) for f in filas]
    finally:
        conn.close()


def obtener_mesa_por_id(mesa_id):
    conn = get_db_connection()
    try:
        fila = conn.execute(
            "SELECT * FROM mesas WHERE id = ?", (mesa_id,)
        ).fetchone()
        return _fila_a_dict(fila)
    finally:
        conn.close()


def crear_mesa(data):
    datos = _normalizar_create(data).model_dump()
    conn = get_db_connection()
    try:
        columnas = ", ".join(datos.keys())
        placeholders = ", ".join("?" * len(datos))
        cursor = conn.execute(
            f"INSERT INTO mesas ({columnas}) VALUES ({placeholders})",
            tuple(datos.values()),
        )
        conn.commit()
        fila = conn.execute(
            "SELECT * FROM mesas WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return _fila_a_dict(fila)
    finally:
        conn.close()


def actualizar_mesa(mesa_id, data):
    cambios = (
        _normalizar_update(data).model_dump(exclude_unset=True)
        if not isinstance(data, MesaUpdate)
        else data.model_dump(exclude_unset=True)
    )
    cambios = {k: v for k, v in cambios.items() if k in EDITABLE_FIELDS}
    conn = get_db_connection()
    try:
        if not cambios:
            fila = conn.execute(
                "SELECT * FROM mesas WHERE id = ?", (mesa_id,)
            ).fetchone()
            return _fila_a_dict(fila)
        asignaciones = ", ".join(f"{k} = ?" for k in cambios)
        cursor = conn.execute(
            f"UPDATE mesas SET {asignaciones} WHERE id = ?",
            (*cambios.values(), mesa_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return None
        fila = conn.execute(
            "SELECT * FROM mesas WHERE id = ?", (mesa_id,)
        ).fetchone()
        return _fila_a_dict(fila)
    finally:
        conn.close()


def eliminar_mesa(mesa_id):
    conn = get_db_connection()
    try:
        cursor = conn.execute("DELETE FROM mesas WHERE id = ?", (mesa_id,))
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()
