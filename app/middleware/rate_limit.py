"""Rate limiting por IP (RNF-22: 100 peticiones/min → 429)."""

import threading
import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

_SKIP_PREFIXES = ("/health", "/live", "/ready", "/metrics", "/docs", "/redoc", "/openapi")


class LimitadorIP:
    """Ventana deslizante: Redis si está disponible, memoria como fallback."""

    def __init__(self, limite=100, ventana=60.0):
        self.limite = limite
        self.ventana = ventana
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def _redis(self):
        try:
            from app.infra.redis import get_redis

            return get_redis()
        except Exception:
            return None

    def puede(self, ip: str, limite: int | None = None, ahora: float | None = None) -> bool:
        techo = limite if limite is not None else self.limite
        r = self._redis()
        if r is not None:
            try:
                clave = f"rl:{ip}:{techo}"
                count = r.incr(clave)
                if count == 1:
                    r.expire(clave, int(self.ventana))
                return count <= techo
            except Exception:
                pass
        # Fallback en memoria (ventana deslizante)
        ahora = ahora if ahora is not None else time.monotonic()
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
    La 429 firma Retry-After (RFC 6585) para que los consumidores no reintente
    a ciegas.
    """

    def __init__(self, app, limite: int = 100):
        super().__init__(app)
        self.contador = LimitadorIP(limite)

    @staticmethod
    def _cliente_real(request) -> str:
        """Auditoría de navegación: el cubo es del CLIENTE REAL.

        Detrás del proxy nginx del despliegue, request.client.host es siempre
        la IP del contenedor frontend: si se usa esa, todos los usuarios
        comparten un único cupo y la navegación normal salta 429 ajenos.
        nginx firma X-Forwarded-For con la IP real del cliente; se toma el
        primer salto (el cliente) y se usa client.host solo como respaldo.
        """
        xff = request.headers.get("x-forwarded-for")
        if xff:
            primer = xff.split(",")[0].strip()
            if primer:
                return primer
        return request.client.host if request.client else "?"

    async def dispatch(self, request, call_next):
        ruta = request.url.path
        if any(ruta.startswith(p) for p in _SKIP_PREFIXES):
            return await call_next(request)

        ip = self._cliente_real(request)
        limite = getattr(request.app.state, "rate_limit_min", self.contador.limite)
        if not self.contador.puede(ip, limite=limite):
            ventana = int(self.contador.ventana)
            return JSONResponse(
                status_code=429,
                headers={"Retry-After": str(ventana)},
                content={
                    "error": {
                        "codigo": 429,
                        "mensaje": "Demasiadas peticiones: espera un momento para seguir.",
                    }
                },
            )
        return await call_next(request)
