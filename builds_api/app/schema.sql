CREATE TABLE IF NOT EXISTS builds (
    id                SERIAL      PRIMARY KEY,
    mesa_id           INTEGER,
    persona           TEXT        NOT NULL,
    handle            TEXT,
    autor             TEXT,
    categoria         TEXT        NOT NULL DEFAULT 'mio',
    nombre            TEXT,
    display           TEXT,
    clase             TEXT,
    raza              TEXT,
    arquetipo         TEXT,
    nivel             INTEGER,
    rol               TEXT,
    alineamiento      TEXT,
    alineamiento_color TEXT,
    privacidad        TEXT        NOT NULL DEFAULT 'publico'
                          CHECK (privacidad IN ('borrador', 'publico', 'privado')),
    actualizado       TEXT,
    protagonista      BOOLEAN     NOT NULL DEFAULT FALSE,
    detalle           TEXT,
    favoritos         INTEGER     NOT NULL DEFAULT 0,
    historial         JSONB       NOT NULL DEFAULT '[]'::jsonb,
    ficha             JSONB,
    creado_en         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_builds_mesa_id ON builds (mesa_id);

CREATE TABLE IF NOT EXISTS tags (
    id     SERIAL PRIMARY KEY,
    nombre TEXT   NOT NULL UNIQUE
);