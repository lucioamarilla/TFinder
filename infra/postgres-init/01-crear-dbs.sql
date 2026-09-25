-- 01-crear-dbs.sql
-- TFinder AE2 (B01): crea las bases por servicio que la imagen postgres
-- no crea por default. La imagen ya crea `mesas_db` via POSTGRES_DB.
--
-- El entrypoint de la imagen corre cada sentencia de los archivos de
-- docker-entrypoint-initdb.d con autocommit, por lo que CREATE DATABASE
-- dentro de un bloque condicional funciona.
--
-- Variante idempotente: si el volumen se resetea sin `down -v` y el script
-- vuelve a correr, las bases ya existentes no generan error.

SELECT 'CREATE DATABASE builds_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'builds_db')\gexec

SELECT 'CREATE DATABASE feed_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'feed_db')\gexec

SELECT 'CREATE DATABASE notif_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'notif_db')\gexec

-- B11: bases de testing (aisladas de las de desarrollo).
SELECT 'CREATE DATABASE mesas_db_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'mesas_db_test')\gexec

SELECT 'CREATE DATABASE builds_db_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'builds_db_test')\gexec

SELECT 'CREATE DATABASE feed_db_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'feed_db_test')\gexec

SELECT 'CREATE DATABASE notif_db_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'notif_db_test')\gexec