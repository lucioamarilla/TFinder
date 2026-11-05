"""Aplicación del DDL idempotente de un servicio (schema.sql).

Los cuatro init_db.py eran idénticos: leer `schema.sql` junto a su módulo y
ejecutarlo sentencia a sentencia (separado por `;` — los comentarios SQL del
DDL no pueden contener punto y coma). La fábrica absorbe ese lazo.
"""

from pathlib import Path


def ejecutar_ddl(pool, ruta_schema):
    ddl = Path(ruta_schema).read_text(encoding="utf-8")
    with pool.connection() as conn:
        for sentencia in ddl.split(";"):
            sentencia = sentencia.strip()
            if sentencia:
                conn.execute(sentencia)
