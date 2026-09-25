import asyncio
import json
import threading

from app.infra.logge import logger


class _Suscriptor:
    def __init__(self, usuario_id=None):
        self.usuario_id = usuario_id
        self.loop = None
        self.cola: "asyncio.Queue[dict]" | None = None


class StreamHub:
    """Hub en memoria que une los consumers (threads) con los clientes SSE.

    `publicar` se llama desde los hilos de consumo; `iterar` se consume desde
    el event loop de FastAPI (StreamingResponse).
    """

    def __init__(self):
        self._suscriptores = []
        self._lock = threading.Lock()

    def suscribir(self, usuario_id=None) -> _Suscriptor:
        s = _Suscriptor(usuario_id)
        with self._lock:
            self._suscriptores.append(s)
        logger.info("ssu: suscriptor conectado", extra={"usuario_id": usuario_id})
        return s

    def desuscribir(self, suscriptor: _Suscriptor):
        with self._lock:
            try:
                self._suscriptores.remove(suscriptor)
            except ValueError:
                pass

    def _encolar(self, cola: "asyncio.Queue[dict]", item: dict):
        try:
            cola.put_nowait(item)
        except asyncio.QueueFull:
            try:
                cola.get_nowait()
            except asyncio.QueueEmpty:
                pass
            try:
                cola.put_nowait(item)
            except asyncio.QueueFull:
                pass

    def publicar(self, usuario_id, notificacion: dict):
        with self._lock:
            targets = [
                s for s in self._suscriptores
                if s.usuario_id is None or s.usuario_id == usuario_id
            ]
        if not targets:
            return
        datos = json.dumps(notificacion, ensure_ascii=False, default=str)
        for s in targets:
            loop = s.loop
            if loop is None or not loop.is_running() or s.cola is None:
                continue
            try:
                loop.call_soon_threadsafe(self._encolar, s.cola, {
                    "usuario_id": usuario_id, "data": datos,
                })
            except RuntimeError:
                pass

    async def iterar(self, suscriptor: _Suscriptor):
        """Generador async: produce eventos SSE (data) o heartbeat mientras dure la conexion."""
        suscriptor.loop = asyncio.get_running_loop()
        suscriptor.cola = asyncio.Queue(maxsize=200)
        heartbeat = False
        while True:
            try:
                item = suscriptor.cola.get_nowait()
                heartbeat = False
                yield f"data: {item['data']}\n\n"
                continue
            except asyncio.QueueEmpty:
                pass
            try:
                item = await asyncio.wait_for(suscriptor.cola.get(), timeout=15.0)
                heartbeat = False
                yield f"data: {item['data']}\n\n"
                continue
            except asyncio.TimeoutError:
                if not heartbeat:
                    yield ": heartbeat\n\n"
                    heartbeat = True
                continue
            except asyncio.CancelledError:
                return
            except Exception as exc:
                logger.error(f"ssu: iterar fallo: {exc!r}")
                return


hub = StreamHub()