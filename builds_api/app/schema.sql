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

-- P1.8: propiedad de builds (RN-11, usuario_id como TEXT del sub del JWT).
ALTER TABLE builds ADD COLUMN IF NOT EXISTS autor_id TEXT;

-- P1.8: tags por build (RF 7.5).
CREATE TABLE IF NOT EXISTS builds_tags (
    build_id INTEGER NOT NULL REFERENCES builds (id) ON DELETE CASCADE,
    nombre   TEXT    NOT NULL REFERENCES tags (nombre) ON DELETE CASCADE,
    PRIMARY KEY (build_id, nombre)
);