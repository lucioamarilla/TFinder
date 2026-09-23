CREATE TABLE IF NOT EXISTS mesas (
    id             SERIAL      PRIMARY KEY,
    nombre         TEXT        NOT NULL,
    sistema        TEXT        NOT NULL,
    descripcion    TEXT,
    tono           TEXT,
    horario        TEXT,
    estado         TEXT        NOT NULL DEFAULT 'abierta'
                               CHECK (estado IN ('abierta', 'cerrada')),
    nivel_inicial  INTEGER,
    jugadores_max  INTEGER,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_mesas_estado ON mesas (estado);