from app.infra.logge import (
    correlation_id_var,
    logger,
    nuevo_correlation_id,
)


class CorrelationMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        cid = None
        for clave, valor in scope["headers"]:
            if clave == b"x-correlation-id":
                cid = valor.decode()
                break
        cid = cid or nuevo_correlation_id()

        token = correlation_id_var.set(cid)
        scope["correlation_id"] = cid

        logger.info("request iniciado", extra={"correlation_id": cid})
        try:

            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.append((b"x-correlation-id", cid.encode()))
                    message = {**message, "headers": headers}
                await send(message)

            await self.app(scope, receive, send_wrapper)
            logger.info("request finalizado", extra={"correlation_id": cid})
        finally:
            correlation_id_var.reset(token)