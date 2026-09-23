from app.infra.redis import get_redis

TTL_RESERVA = 60


def reservar(mesa_id: int) -> bool:
    r = get_redis()
    ok = r.set(f"reserva:vacante:{mesa_id}", "1", nx=True, ex=TTL_RESERVA)
    return bool(ok)


def liberar(mesa_id: int):
    get_redis().delete(f"reserva:vacante:{mesa_id}")