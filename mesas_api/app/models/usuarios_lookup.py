"""F3: lookup de usuarios por id (para bitácora y nombres de autor)."""

from mesas_api.app.db import get_connection


def obtener_usuario_por_id(usuario_id: int):
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT id, email, nombre, rol, avatar_url, bio FROM usuarios WHERE id = %s",
            (usuario_id,),
        ).fetchone()
        return dict(fila) if fila else None


def actualizar_perfil(usuario_id: int, nombre=None, bio=None, avatar_url=None):
    cambios, params = [], []
    if nombre is not None:
        if not str(nombre).strip():
            raise ValueError("El nombre es obligatorio.")
        cambios.append("nombre = %s")
        params.append(str(nombre).strip())
    if bio is not None:
        cambios.append("bio = %s")
        params.append(bio)
    if avatar_url is not None:
        cambios.append("avatar_url = %s")
        params.append(avatar_url)
    if not cambios:
        return obtener_usuario_por_id(usuario_id)
    with get_connection() as conn:
        cursor = conn.execute(
            f"UPDATE usuarios SET {', '.join(cambios)} WHERE id = %s RETURNING id",
            (*params, usuario_id),
        )
        if cursor.rowcount == 0:
            return None
        fila = conn.execute(
            "SELECT id, email, nombre, rol, avatar_url, bio FROM usuarios WHERE id = %s",
            (usuario_id,),
        ).fetchone()
        return dict(fila)
