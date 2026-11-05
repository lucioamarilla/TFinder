"""DDL del dueño de notif_db: ver schema.sql en esta carpeta."""

import os

from app.infra.ddl import ejecutar_ddl
from notif_api.app.db import get_pool


def init_db():
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
    ejecutar_ddl(get_pool(), ruta)
