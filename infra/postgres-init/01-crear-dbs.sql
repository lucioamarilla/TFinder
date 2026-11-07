-- 01-crear-dbs.sql
-- TFinder (solo mesas): crea la base de tests para mesas.
-- La imagen ya crea `mesas_db` via POSTGRES_DB.

SELECT 'CREATE DATABASE mesas_db_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'mesas_db_test')\gexec