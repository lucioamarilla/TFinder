from builds_api.app.db import get_connection
from builds_api.app.schemas import BuildOut


class BuildNotFoundError(Exception):
    def __init__(self, build_id):
        self.build_id = build_id
        super().__init__(f"Build {build_id} no encontrado")


class BuildProhibidoError(Exception):
    """403 (VAL-38/RN-11): solo el creador edita/elimina su build."""


class ValorInvalidoError(Exception):
    """400 (VAL-44/45): clase obligatoria y atributos 3..18."""


def _serializar(fila):
    f = dict(fila)
    f["mesaId"] = f.pop("mesa_id", None)
    f["autorId"] = f.pop("autor_id", None)
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

# ---- P1.8: escritura de builds (RF-19/20/21, RN-11/12/19, VAL-44/45) ----------

import json as _json
from typing import Optional

from fastapi import HTTPException

from app.infra.mesas import es_miembro_aceptado  # puente B09 compartido


_VALIDACION_NUMERICA = {
    "fue": "Fuerza",
    "des": "Destreza",
    "con": "Constitución",
    "int": "Inteligencia",
    "sab": "Sabiduría",
    "car": "Carisma",
}


def _campos_de_ficha(datos):
    return {
        "persona": (datos.get("titulo") or datos.get("persona") or "").strip() or "Personaje",
        "nombre": datos.get("nombre") or datos.get("titulo"),
        "clase": (datos.get("clase") or "").strip() or None,
        "raza": datos.get("raza"),
        "arquetipo": datos.get("arquetipo"),
        "nivel": datos.get("nivel"),
        "rol": datos.get("rol"),
        "alineamiento": datos.get("alineamiento"),
        "detalle": datos.get("detalle"),
    }


def _validar(datos: dict, requerir_clase: bool = False):
    """RF-19 / VAL-44 / VAL-45. En updates solo valida lo que viene."""
    clase = datos.get("clase")
    if clase is not None:
        if not str(clase).strip():
            raise ValorInvalidoError("La clase del personaje es obligatoria.")
    elif requerir_clase:
        raise ValorInvalidoError("La clase del personaje es obligatoria.")
    nivel = datos.get("nivel")
    if nivel is not None and (not isinstance(nivel, int) or nivel < 1 or nivel > 20):
        raise ValorInvalidoError("El nivel debe estar entre 1 y 20.")
    atributos = datos.get("atributos")
    ficha_val = datos.get("ficha")
    if isinstance(ficha_val, dict) and ficha_val.get("atributos"):
        atributos = ficha_val["atributos"]
    if isinstance(atributos, dict):
        for clave, nombre in _VALIDACION_NUMERICA.items():
            valor = atributos.get(clave)
            if valor is None:
                continue
            if not isinstance(valor, int) or not 3 <= valor <= 18:
                raise ValorInvalidoError(f"El atributo {nombre} debe estar entre 3 y 18.")
    return datos


def _propietario_o_403(usuario, fila):
    autor_id = fila.get("autor_id")
    if (usuario or {}).get("rol") == "admin":
        return
    if autor_id is None or str(usuario["sub"]) != str(autor_id):
        raise BuildProhibidoError("No tienes permisos para este build: es de otro creador.")


def crear_build(usuario, datos, token=None):
    datos = _validar(dict(datos), requerir_clase=True)
    ficha = datos.get("atributos") or datos.get("ficha")
    with get_connection() as conn:
        fila = conn.execute(
            """
            INSERT INTO builds (
                persona, handle, autor, nombre, display, clase, raza, arquetipo,
                nivel, rol, alineamiento, privacidad, detalle, ficha, autor_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s
            ) RETURNING *""",
            (
                datos.get("persona") or datos.get("titulo") or "Personaje",
                datos.get("handle") or f"@{ (datos.get('titulo') or 'pj').lower().replace(' ', '_') }",
                usuario.get("email"),
                datos.get("nombre") or datos.get("titulo"),
                datos.get("titulo"),
                (datos.get("clase") or "").strip() or None,
                datos.get("raza"),
                datos.get("arquetipo"),
                datos.get("nivel"),
                datos.get("rol"),
                datos.get("alineamiento"),
                "borrador",
                datos.get("detalle"),
                _json.dumps(datos.get("ficha") if isinstance(datos.get("ficha"), dict) else ({"atributos": datos.get("atributos")} if datos.get("atributos") else {})),
                str(usuario["sub"]),
            ),
        ).fetchone()
    return _serializar(fila)


def _fila_cruda(build_id):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM builds WHERE id = %s", (build_id,)).fetchone()


def actualizar_build(build_id, usuario, datos, token=None):
    """RN-11/VAL-38 (+ RN-19): edita, valida y APILA la versión previa en historial."""
    _validar({**datos})
    fila = _fila_cruda(build_id)
    if fila is None:
        raise BuildNotFoundError(build_id)
    _propietario_o_403(usuario, fila)

    campos = _campos_de_ficha({**dict(fila), **datos})
    historial = list(fila["historial"] or [])
    historial.append(
        {
            "version": len(historial) + 1,
            "at": fila.get("actualizado"),
            "snapshot": {k: fila.get(k) for k in ("clase", "raza", "arquetipo", "nivel", "rol", "ficha")},
        }
    )
    with get_connection() as conn, conn.transaction():
        updated = conn.execute(
            """
            UPDATE builds SET persona = %s, nombre = %s, clase = %s, raza = %s,
                arquetipo = %s, nivel = %s, rol = %s, alineamiento = %s,
                detalle = %s, ficha = %s, historial = %s, actualizado = to_char(now(), 'YYYY-MM-DD"T"HH24:MI:SS')
            WHERE id = %s RETURNING *""",
            (
                campos["persona"], campos["nombre"], campos["clase"], campos["raza"],
                campos["arquetipo"], campos["nivel"], campos["rol"], campos["alineamiento"],
                campos["detalle"],
                _json.dumps(datos["ficha"]) if isinstance(datos.get("ficha"), dict)
                else (_json.dumps(fila["ficha"]) if fila["ficha"] else None),
                _json.dumps(historial),
                build_id,
            ),
        ).fetchone()
    return _serializar(updated)


def restaurar_build(build_id, indice, usuario):
    """RN-19: restaurar una versión anterior del historial."""
    fila = _fila_cruda(build_id)
    if fila is None:
        raise BuildNotFoundError(build_id)
    _propietario_o_403(usuario, fila)
    historial = list(fila["historial"] or [])
    if not historial or indice < 0 or indice >= len(historial):
        raise HTTPException(status_code=404, detail="No existe esa versión.")
    snapshot = historial[indice]["snapshot"]
    actualizar = {k: v for k, v in snapshot.items() if v is not None}
    return actualizar_build(build_id, usuario, actualizar, token=None)


def eliminar_build(build_id, usuario):
    fila = _fila_cruda(build_id)
    if fila is None:
        raise BuildNotFoundError(build_id)
    _propietario_o_403(usuario, fila)
    with get_connection() as conn:
        conn.execute("DELETE FROM builds WHERE id = %s", (build_id,))


def publicar_build(build_id, usuario):
    """RF-20/RN-14: publica el build propio (lo vuelve público)."""
    fila = _fila_cruda(build_id)
    if fila is None:
        raise BuildNotFoundError(build_id)
    _propietario_o_403(usuario, fila)
    with get_connection() as conn:
        actualizado = conn.execute(
            "UPDATE builds SET privacidad = 'publico' WHERE id = %s RETURNING *",
            (build_id,),
        ).fetchone()
    return _serializar(actualizado)


def vincular_build(build_id, mesa_id, usuario, token=None):
    """RF-21/RN-12/VAL-40: el creador debe ser miembro aceptado de la mesa."""
    fila = _fila_cruda(build_id)
    if fila is None:
        raise BuildNotFoundError(build_id)
    _propietario_o_403(usuario, fila)
    try:
        miembro = es_miembro_aceptado(int(mesa_id), usuario, token=token)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from None
    if not miembro:
        raise HTTPException(status_code=403, detail="No eres miembro de esta mesa.")
    with get_connection() as conn:
        actualizado = conn.execute(
            "UPDATE builds SET mesa_id = %s WHERE id = %s RETURNING *",
            (int(mesa_id), build_id),
        ).fetchone()
    return _serializar(actualizado)


def desvincular_build(build_id, usuario, token=None):
    fila = _fila_cruda(build_id)
    if fila is None:
        raise BuildNotFoundError(build_id)
    _propietario_o_403(usuario, fila)
    with get_connection() as conn:
        actualizado = conn.execute(
            "UPDATE builds SET mesa_id = NULL WHERE id = %s RETURNING *",
            (build_id,),
        ).fetchone()
    return _serializar(actualizado)


def asignar_tags(build_id, usuario, nombres, token=None):
    fila = _fila_cruda(build_id)
    if fila is None:
        raise BuildNotFoundError(build_id)
    _propietario_o_403(usuario, fila)
    with get_connection() as conn, conn.transaction():
        for nombre in nombres or []:
            limpio = (nombre or "").strip()
            if not limpio:
                continue
            conn.execute("INSERT INTO tags (nombre) VALUES (%s) ON CONFLICT DO NOTHING", (limpio,))
            conn.execute(
                "INSERT INTO builds_tags (build_id, nombre) VALUES (%s, %s)"
                " ON CONFLICT DO NOTHING",
                (build_id, limpio),
            )
        filas = conn.execute(
            "SELECT nombre FROM builds_tags WHERE build_id = %s ORDER BY nombre", (build_id,)
        ).fetchall()
    return {"build_id": build_id, "tags": [f["nombre"] for f in filas]}


def listar_builds_filtradas(mesa_id=None, autor_id=None, tag=None):
    """Listado con filtro de visibilidad (RN-11: privado/borrador ajenos no salen)."""
    conditions, params = [], []
    if mesa_id is not None:
        conditions.append("b.mesa_id = %s")
        params.append(mesa_id)
    if autor_id:
        conditions.append("b.autor_id = %s")
        params.append(str(autor_id))
    if tag:
        conditions.append(
            "b.id IN (SELECT build_id FROM builds_tags WHERE nombre = %s)"
        )
        params.append(tag)
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    with get_connection() as conn:
        filas = conn.execute(
            f"SELECT * FROM builds b {where} ORDER BY b.id", params
        ).fetchall()
    return [_serializar(f) for f in filas]
