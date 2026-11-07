from mesas_api.app.db import get_connection
from mesas_api.app.schemas import EDITABLE_FIELDS, MesaCreate, MesaUpdate


def _normalizar_create(data):
    if isinstance(data, MesaCreate):
        return data
    return MesaCreate(**data)


def listar_mesas(
    estado=None, sistema=None, tono=None, orden="id", page=1, limit=20
):
    """Listado con filtros (RF-04/RF-13) y paginación (techo 50)."""
    ordenes = {
        "id": "id ASC",
        "recientes": "fecha_creacion DESC, id DESC",
        "nombre": "nombre ASC, id ASC",
    }
    where, params = [], []
    if estado:
        where.append("estado = %s")
        params.append(estado)
    if sistema:
        where.append("sistema = %s")
        params.append(sistema)
    if tono:
        where.append("tono ILIKE %s")
        params.append(f"%{tono}%")
    sql = (
        "SELECT m.*, u.nombre AS gm_nombre,"
        " (SELECT COUNT(*) FROM miembros_mesa mm WHERE mm.mesa_id = m.id AND mm.rol = 'jugador') AS jugadores_calc"
        " FROM mesas m"
        " LEFT JOIN usuarios u ON u.id = m.gm_id"
    )
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += f" ORDER BY {ordenes[orden]} LIMIT %s OFFSET %s"
    params += [limit, (page - 1) * limit]
    with get_connection() as conn:
        filas = conn.execute(sql, params).fetchall()
        resultado = []
        for fila in filas:
            d = dict(fila)
            d["jugadores_actuales"] = d.pop("jugadores_calc", d.get("jugadores_actuales", 0))
            resultado.append(d)
        return resultado


def obtener_mesa_por_id(mesa_id):
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT m.*, u.nombre AS gm_nombre,"
            " (SELECT COUNT(*) FROM miembros_mesa mm WHERE mm.mesa_id = m.id AND mm.rol = 'jugador') AS jugadores_calc"
            " FROM mesas m"
            " LEFT JOIN usuarios u ON u.id = m.gm_id"
            " WHERE m.id = %s",
            (mesa_id,),
        ).fetchone()
        if not fila:
            return None
        d = dict(fila)
        d["jugadores_actuales"] = d.pop("jugadores_calc", d.get("jugadores_actuales", 0))
        return d


def crear_mesa(data, gm_id: int):
    datos = _normalizar_create(data).model_dump()
    datos["gm_id"] = gm_id
    columnas = ", ".join(datos.keys())
    placeholders = ", ".join(["%s"] * len(datos))
    with get_connection() as conn, conn.transaction():
        cursor = conn.execute(
            f"INSERT INTO mesas ({columnas}) VALUES ({placeholders}) RETURNING id",
            tuple(datos.values()),
        )
        mesa_id = cursor.fetchone()["id"]
        # F2 (2.1): el creador pasa a ser master de la mesa automáticamente.
        conn.execute(
            "INSERT INTO miembros_mesa (mesa_id, usuario_id, rol) VALUES (%s, %s, 'master')",
            (mesa_id, gm_id),
        )
        # D-17: devolver la fila con el nombre visible del GM (mismo contrato
        # que listar/obtener: JOIN usuarios) para que el frontend no muestre
        # el GM vacio hasta recargar.
        fila = conn.execute(
            "SELECT m.*, u.nombre AS gm_nombre FROM mesas m"
            " LEFT JOIN usuarios u ON u.id = m.gm_id WHERE m.id = %s",
            (mesa_id,),
        ).fetchone()
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


def ocupar_vacante(mesa_id) -> bool:
    """Check-and-set atómico: solo la transacción que pasa el WHERE devuelve fila.

    En Postgres el UPDATE toma lock de fila hasta el commit; dos solicitudes
    concurrentes se serializan y solo una gana el cupo.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE mesas SET jugadores_actuales = jugadores_actuales + 1"
            " WHERE id = %s AND (jugadores_max IS NULL OR jugadores_actuales < jugadores_max)"
            " RETURNING id",
            (mesa_id,),
        )
        return cursor.fetchone() is not None


def liberar_vacante(mesa_id):
    """Devuelve una vacante (expulsión/baja). Nunca baja de 0."""
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE mesas SET jugadores_actuales = greatest(jugadores_actuales - 1, 0)"
            " WHERE id = %s RETURNING jugadores_actuales",
            (mesa_id,),
        )
        fila = cursor.fetchone()
        return fila["jugadores_actuales"] if fila else None


def rol_de(usuario_id: int, mesa_id: int):
    """F2: rol contextual del usuario en la mesa (master | jugador | None)."""
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT rol FROM miembros_mesa WHERE mesa_id = %s AND usuario_id = %s",
            (mesa_id, usuario_id),
        ).fetchone()
        return fila["rol"] if fila else None


def listar_con_rol(usuario_id: int):
    """Mesas del usuario como master (creador) o como jugador miembro (F1)."""
    with get_connection() as conn:
        filas = conn.execute(
            """
            SELECT m.*,
                   (SELECT COUNT(*) FROM miembros_mesa mm WHERE mm.mesa_id = m.id AND mm.rol = 'jugador') AS jugadores_calc,
                   CASE WHEN m.gm_id = %s THEN 'master' ELSE 'jugador' END AS mi_rol
            FROM mesas m
            WHERE m.gm_id = %s
               OR m.id IN (
                   SELECT s.mesa_id FROM solicitudes_uniones s
                   WHERE s.usuario_id = %s AND s.estado = 'aceptada'
               )
            ORDER BY m.fecha_creacion DESC, m.id DESC
            """,
            (usuario_id, usuario_id, usuario_id),
        ).fetchall()
        resultado = []
        for fila in filas:
            d = dict(fila)
            d["jugadores_actuales"] = d.pop("jugadores_calc", d.get("jugadores_actuales", 0))
            resultado.append(d)
        return resultado