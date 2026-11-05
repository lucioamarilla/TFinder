"""Métricas de Prometheus (RNF-20): contadores de negocio por servicio.

Formato exposicion texto v0.0.4 sin dependencias externas:
    # HELP tf_requests_total Peticiones HTTP por clase de estado.
    # TYPE tf_requests_total counter
    tf_requests_total{servicio="mesas",estado="2xx"} 42
"""

import threading

_lock = threading.Lock()
_contadores: dict[tuple[str, str], int] = {}  # (servicio, clase_estado) -> N


def contar(servicio: str, estado: int):
    clase = f"{estado // 100}xx" if estado >= 100 else "?"
    with _lock:
        key = (servicio, clase)
        _contadores[key] = _contadores.get(key, 0) + 1


def exposicion(servicio: str) -> str:
    with _lock:
        copia = dict(_contadores)
    lineas = [
        "# HELP tf_requests_total Peticiones HTTP por clase de estado.",
        "# TYPE tf_requests_total counter",
    ]
    total = 0
    for (s, clase), valor in sorted(copia.items()):
        if s != servicio:
            continue
        lineas.append(
            f'tf_requests_total{{servicio="{s}",estado="{clase}"}} {valor}'
        )
        total += valor
    if not any(s == servicio for (s, _) in copia):
        lineas.append(f'tf_requests_total{{servicio="{servicio}",estado="0xx"}} 0')
        total = 0
    lineas.append(f'tf_acumulado_total{{servicio="{servicio}"}} {total}')
    return "\n".join(lineas) + "\n"
