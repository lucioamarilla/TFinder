import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_path():
    url = os.getenv("DATABASE_URL", "sqlite:///./tfinder.db")
    return url.replace("sqlite:///", "", 1)


def get_db_connection():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    schema_path = os.path.join(BASE_DIR, "schema.sql")
    with open(schema_path, encoding="utf-8") as f:
        ddl = f.read()
    conn = get_db_connection()
    try:
        conn.executescript(ddl)
        _aplicar_migraciones(conn)
        conn.commit()
    finally:
        conn.close()


def _aplicar_migraciones(conn):
    version = conn.execute("PRAGMA user_version").fetchone()[0]

    if version < 1:
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_mesas_estado ON mesas (estado)"
        )
        conn.execute("PRAGMA user_version = 1")