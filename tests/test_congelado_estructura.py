"""CONGELADO: invariantes de arquitectura que el refactor NO debe romper.

- RNF-04 (propiedad de datos): ninguna URL de base puede vivir fuera del
  db.py del servicio dueño.
- Valores vitales de Redis/TTLs (cache 60s, llamado 120s, QR 600s).
- Defaults de configuración por servicio.
"""

import re
from pathlib import Path

CACHE_MESAS_TTL = 60
TTL_LLAMADO_SEG = 120
TTL_QR = 600
URLS_DEFAULT = {
    "mesas_api": "postgresql://tfinder:tfinder@localhost:5432/mesas_db",
    "builds_api": "postgresql://tfinder:tfinder@localhost:5432/builds_db",
    "feed_api": "postgresql://tfinder:tfinder@localhost:5432/feed_db",
    "notif_api": "postgresql://tfinder:tfinder@localhost:5432/notif_db",
}
PUERTOS_DEFAULT = {"mesas_api": "8001", "builds_api": "8002", "feed_api": "8003", "notif_api": "8004"}


def test_rnf04_urls_de_base_solo_en_db_py_de_cada_servicio():
    raiz = Path()
    violaciones = []
    for ruta in raiz.glob("*/*/**/*.py"):
        partes = ruta.parts
        if partes[0] in ("tests", ".venv") or "__pycache__" in partes:
            continue
        if partes[-1] == "db.py" and len(partes) >= 3 and partes[1] == "app":
            continue  # el db.py del servicio dueño es EL lugar legítimo
        texto = ruta.read_text(encoding="utf-8", errors="ignore")
        for linea in texto.splitlines():
            if re.search(r"postgresql://[^\s\"']*_(db)\b", linea):
                violaciones.append((str(ruta), linea.strip()))
    assert violaciones == [], f"RNF-04 roto: {violaciones[:5]}"


def test_urls_de_base_de_cada_servicio_congeladas():
    assert (Path("mesas_api") / "app" / "db.py").read_text().count(
        URLS_DEFAULT["mesas_api"]
    ) >= 1
    assert (Path("builds_api") / "app" / "db.py").read_text().count(
        URLS_DEFAULT["builds_api"]
    ) >= 1
    assert (Path("feed_api") / "app" / "db.py").read_text().count(
        URLS_DEFAULT["feed_api"]
    ) >= 1
    assert (Path("notif_api") / "app" / "db.py").read_text().count(
        URLS_DEFAULT["notif_api"]
    ) >= 1


def test_ttls_de_negocio_congelados():
    from mesas_api.app.services.cache import CACHE_MESAS_TTL, PREFIJO
    from mesas_api.app.services.llamado import TTL_LLAMADO_SEG
    from mesas_api.app.services.qr_asistencia import TTL_QR

    assert CACHE_MESAS_TTL == 60
    assert PREFIJO == "cache:mesas:list"
    assert TTL_LLAMADO_SEG == 120
    assert TTL_QR == 600


def test_claves_redis_congeladas():
    texto_cache = (Path("mesas_api") / "app" / "services" / "cache.py").read_text()
    assert "'cache:mesas:list'" in texto_cache or '"cache:mesas:list"' in texto_cache
    texto_llamado = (Path("mesas_api") / "app" / "services" / "llamado.py").read_text()
    assert "llamado:" in texto_llamado
    texto_qr = (Path("mesas_api") / "app" / "services" / "qr_asistencia.py").read_text()
    assert "qr:sesion:" in texto_qr
    texto_auth = (Path("mesas_api") / "app" / "models" / "auth_model.py").read_text()
    assert "sesion:" in texto_auth


def test_puertos_por_servicio_congelados():
    for servicio, puerto in PUERTOS_DEFAULT.items():
        texto = (Path(servicio) / "app" / "config.py").read_text()
        assert f'"{puerto}"' in texto, f"{servicio}: default de puerto cambió"
