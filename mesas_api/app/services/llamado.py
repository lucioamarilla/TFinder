from app.infra.redis import get_redis

TTL_LLAMADO_SEG = 120


def abrir_llamado(matchmaking_id: int) -> dict:
    r = get_redis()
    r.setex(f"llamado:{matchmaking_id}", TTL_LLAMADO_SEG, "abierto")
    return {
        "matchmaking_id": matchmaking_id,
        "estado": "abierto",
        "expira_en": TTL_LLAMADO_SEG,
    }


def estado_llamado(matchmaking_id: int) -> dict:
    r = get_redis()
    clave = f"llamado:{matchmaking_id}"
    if r.exists(clave):
        return {"estado": "abierto", "ttl_restante": r.ttl(clave)}
    return {"estado": "cerrado", "ttl_restante": 0}