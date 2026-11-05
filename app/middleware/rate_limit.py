"""Rate limiting por IP (RNF-22: 100 peticiones/min → 429)."""

import threading
import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

_SKIP_PREFIXES = ("/health", "/live", "/ready", "/metrics", "/docs", "/redoc", "/openapi")


class LimitadorIP:
    """Ventana deslizante en memoria (una instancia por proceso)."""

    def __init__(self, limite=100, ventana=60.0):
        self.limite = limite
        self.ventana = ventana
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def puede(self, ip: str, limite: int | None = None, ahora: float | None = None) -> bool:
        ahora = ahora if ahora is not None else time.monotonic()
        techo = limite if limite is not None else self.limite
        with self._lock:
            cola = self._hits[ip]
            corte = ahora - self.ventana
            while cola and cola[0] <= corte:
                cola.popleft()
            if len(cola) >= techo:
                return False
            cola.append(ahora)
            return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    """100 req/min por IP (RNF-22). El techo dinámico se calibra para pruebas.

    Una sobrecarga con aborto con HTTP 429 y el envelope estándar:
        {"error": {"codigo": 429, "mensaje": "Demasiadas peticiones..."}}
    """

    def __init__(self, app, limite: int = 100):
        super().__init__(app)
        self.contador = LimitadorIP(limite)

    async def dispatch(self, request, call_next):
        ruta = request.url.path
        if any(ruta.startswith(p) for p in _SKIP_PREFIXES):
            return await call_next(request)

        ip = request.client.host if request.client else request.headers.get("x-forwarded-for", "?")
        limite = getattr(request.app.state, "rate_limit_min", self.contador.limite)
        if not self.contador.puede(ip, limite=limite):
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "codigo": 429,
                        "mensaje": "Demasiadas peticiones: espera un momento para seguir.",
                    }
                },
            )
        return await call_next(request)
