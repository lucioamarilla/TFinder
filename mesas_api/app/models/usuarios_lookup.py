"""F3: lookup de usuarios por id (para bitácora y nombres de autor)."""

from mesas_api.app.db import get_connection


def obtener_usuario_por_id(usuario_id: int):
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT id, email, nombre, rol FROM usuarios WHERE id = %s",
            (usuario_id,),
        ).fetchone()
        return dict(fila) if fila else None
