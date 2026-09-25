from builds_api.app.db import get_connection
from builds_api.app.schemas import BuildOut


class BuildNotFoundError(Exception):
    def __init__(self, build_id):
        self.build_id = build_id
        super().__init__(f"Build {build_id} no encontrado")


def _serializar(fila):
    f = dict(fila)
    f["mesaId"] = f.pop("mesa_id", None)
    f["alineamientoColor"] = f.pop("alineamiento_color", None)
    f.pop("creado_en", None)
    return BuildOut(**f)


def listar_builds(mesa_id=None):
    with get_connection() as conn:
        if mesa_id is not None:
            filas = conn.execute(
                "SELECT * FROM builds WHERE mesa_id = %s ORDER BY id", (mesa_id,)
            ).fetchall()
        else:
            filas = conn.execute("SELECT * FROM builds ORDER BY id").fetchall()
    return [_serializar(f) for f in filas]


def obtener_build(build_id):
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT * FROM builds WHERE id = %s", (build_id,)
        ).fetchone()
    if fila is None:
        raise BuildNotFoundError(build_id)
    return _serializar(fila)