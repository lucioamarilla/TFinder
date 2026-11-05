from app.infra.rabbitmq import publicar


def publicar_solicitud(mesa_id: int, usuario_id: int, correlation_id: str = "-"):
    return publicar(
        "mesa.solicitada",
        {"mesa_id": mesa_id, "usuario_id": usuario_id},
        correlation_id=correlation_id,
    )


def publicar_aceptacion(mesa_id: int, usuario_id: int, correlation_id: str = "-"):
    return publicar(
        "mesa.aceptada",
        {"mesa_id": mesa_id, "usuario_id": usuario_id},
        correlation_id=correlation_id,
    )


def publicar_expulsion(mesa_id: int, usuario_id: int, correlation_id: str = "-"):
    return publicar(
        "mesa.expulsada",
        {"mesa_id": mesa_id, "usuario_id": usuario_id},
        correlation_id=correlation_id,
    )


def publicar_sesion_confirmada(
    mesa_id: int, sesion_id: int, usuario_id: int, correlation_id: str = "-"
):
    """Emite sesion.confirmada (B07/proveedor-email).

    notif-api la consume: persiste la notificación del usuario, la emite por
    SSE y envía el email "Sesión confirmada" a los miembros de la mesa.
    """
    return publicar(
        "sesion.confirmada",
        {"mesa_id": mesa_id, "sesion_id": sesion_id, "usuario_id": usuario_id},
        correlation_id=correlation_id,
    )