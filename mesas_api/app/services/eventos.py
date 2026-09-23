from app.infra.rabbitmq import publicar


def publicar_solicitud(mesa_id: int, usuario_id: int):
    return publicar("mesa.solicitada", {"mesa_id": mesa_id, "usuario_id": usuario_id})


def publicar_aceptacion(mesa_id: int, usuario_id: int):
    return publicar("mesa.aceptada", {"mesa_id": mesa_id, "usuario_id": usuario_id})


def publicar_expulsion(mesa_id: int, usuario_id: int):
    return publicar("mesa.expulsada", {"mesa_id": mesa_id, "usuario_id": usuario_id})