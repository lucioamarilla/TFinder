"""Controller del calendario con votación (P1.5, RF-10/RF-11)."""

from datetime import datetime, timezone

from fastapi import HTTPException

from mesas_api.app.models.fechas import (
    PropuestaPasadaError,
    confirmar_fecha,
    descartar_fecha,
    es_miembro_jugador,
    listar_fechas,
    obtener_fecha,
    proponer_fecha,
    votar_fecha,
)


def _es_gm(usuario, mesa) -> bool:
    return mesa.get("gm_id") is not None and int(usuario["sub"]) == mesa["gm_id"]


def _mesa_o_404(mesa_id):
    from mesas_api.app.models.mesa import obtener_mesa_por_id

    mesa = obtener_mesa_por_id(mesa_id)
    if mesa is None:
        raise HTTPException(status_code=404, detail=f"Mesa {mesa_id} no encontrada")
    return mesa


def _iso(valor):
    if isinstance(valor, datetime):
        return valor.isoformat()
    return str(valor)


def proponer_controller(mesa_id, usuario, payload_propuesta):
    mesa = _mesa_o_404(mesa_id)
    if not _es_gm(usuario, mesa):
        raise HTTPException(
            status_code=403,
            detail="Solo el GM propietario puede proponer fechas de sesión.",
        )
    try:
        fila = proponer_fecha(mesa_id, payload_propuesta, int(usuario["sub"]))
    except PropuestaPasadaError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    return {**fila, "propuesta": _iso(fila["propuesta"]), "votos": {"a_favor": 0, "en_contra": 0}}


def listar_controller(mesa_id, _usuario):
    _mesa_o_404(mesa_id)
    return [
        {
            "id": f["id"],
            "mesa_id": f["mesa_id"],
            "propuesta": _iso(f["propuesta"]),
            "estado": f["estado"],
            "votos": {"a_favor": int(f["a_favor"]), "en_contra": int(f["en_contra"])},
            "a_favor_nombres": (f.get("a_favor_nombres") or "").split(", ") if f.get("a_favor_nombres") else [],
            "en_contra_nombres": (f.get("en_contra_nombres") or "").split(", ") if f.get("en_contra_nombres") else [],
        }
        for f in listar_fechas(mesa_id)
    ]


def votar_controller(mesa_id, fecha_id, usuario, valor):
    if valor not in ("a_favor", "en_contra"):
        raise HTTPException(status_code=400, detail="El voto debe ser 'a favor' o 'en contra'.")
    mesa = _mesa_o_404(mesa_id)
    fila = obtener_fecha(mesa_id, fecha_id)
    if fila is None:
        raise HTTPException(status_code=404, detail="La fecha no existe.")
    if fila["estado"] != "propuesta":
        raise HTTPException(status_code=409, detail="Esta fecha ya no acepta votos.")
    if _es_gm(usuario, mesa):
        raise HTTPException(
            status_code=403,
            detail="El GM no vota las fechas que propone.",
        )
    if not es_miembro_jugador(mesa_id, int(usuario["sub"])):
        raise HTTPException(status_code=403, detail="No eres miembro de esta mesa.")
    votar_fecha(fecha_id, int(usuario["sub"]), valor)
    return {
        "id": fecha_id,
        "valor": valor,
        "votos": _votos_de(mesa_id, fecha_id),
    }


def _votos_de(mesa_id, fecha_id):
    for f in listar_fechas(mesa_id):
        if f["id"] == fecha_id:
            return {"a_favor": int(f["a_favor"]), "en_contra": int(f["en_contra"])}
    return {"a_favor": 0, "en_contra": 0}


def descartar_controller(mesa_id, fecha_id, usuario):
    mesa = _mesa_o_404(mesa_id)
    if not _es_gm(usuario, mesa):
        raise HTTPException(
            status_code=403,
            detail="Solo el GM propietario descarta propuestas de fecha.",
        )
    fila = obtener_fecha(mesa_id, fecha_id)
    if fila is None:
        raise HTTPException(status_code=404, detail="La fecha no existe.")
    descartar_fecha(fecha_id)
    return {"id": fecha_id, "estado": "descartada"}


def confirmar_controller(mesa_id, fecha_id, usuario):
    mesa = _mesa_o_404(mesa_id)
    fila = obtener_fecha(mesa_id, fecha_id)
    if fila is None:
        raise HTTPException(status_code=404, detail="La fecha no existe.")
    if not _es_gm(usuario, mesa):
        raise HTTPException(
            status_code=403,
            detail="Solo el GM propietario confirma la fecha ganadora.",
        )
    resultado = confirmar_fecha(fecha_id, mesa_id)
    if resultado is None:
        raise HTTPException(status_code=409, detail="Esta fecha ya fue cerrada.")
    return {
        "id": fila["id"],
        "mesa_id": mesa_id,
        "estado": "confirmada",
        "propuesta": _iso(resultado["propuesta"]["propuesta"]),
        "sesion_id": resultado["sesion"]["id"],
    }
