CREATE TABLE IF NOT EXISTS publicaciones (
    id               SERIAL      PRIMARY KEY,
    tipo             TEXT        NOT NULL DEFAULT 'post'
                                 CHECK (tipo IN ('post', 'build', 'wiki')),
    autor            TEXT,
    autor_id         TEXT,
    autor_nombre     TEXT,
    iniciales        TEXT,
    tono             TEXT,
    tiempo           TEXT,
    horas            INTEGER     NOT NULL DEFAULT 0,
    etiqueta         TEXT,
    titulo           TEXT        NOT NULL,
    cuerpo           TEXT,
    votos            INTEGER     NOT NULL DEFAULT 0,
    total_comentarios INTEGER    NOT NULL DEFAULT 0,
    embed            JSONB,
    comentarios      JSONB       NOT NULL DEFAULT '[]'::jsonb,
    creado_en        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS wiki_paginas (
    id        SERIAL      PRIMARY KEY,
    mesa_id   TEXT        NOT NULL,
    carpeta   TEXT        NOT NULL DEFAULT 'notas',
    titulo    TEXT        NOT NULL,
    tipo      TEXT        NOT NULL DEFAULT 'NOTA',
    fecha     TEXT,
    resumen   TEXT,
    contenido JSONB       NOT NULL DEFAULT '[]'::jsonb,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_wiki_mesa_id ON wiki_paginas (mesa_id);

-- P1.6: visibilidad por página (RN-05: privada | jugadores | publica).
ALTER TABLE wiki_paginas ADD COLUMN IF NOT EXISTS visibilidad TEXT NOT NULL DEFAULT 'jugadores';

-- P1.7: feed activo — likes únicos y follows (RF-17/RF-18).
CREATE TABLE IF NOT EXISTS likes_post (
    post_id    INTEGER     NOT NULL REFERENCES publicaciones (id) ON DELETE CASCADE,
    usuario_id TEXT        NOT NULL,
    fecha      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (post_id, usuario_id)
);

-- F1: comunidades reales (t/<nombre>) como texto del campo comunidad.
ALTER TABLE publicaciones ADD COLUMN IF NOT EXISTS comunidad TEXT;

CREATE TABLE IF NOT EXISTS follows (
    id          SERIAL      PRIMARY KEY,
    seguidor_id TEXT        NOT NULL,
    seguido_id  TEXT        NOT NULL,
    fecha       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_follows_par
    ON follows (seguidor_id, seguido_id);
CREATE INDEX IF NOT EXISTS idx_follows_seguido ON follows (seguido_id);
-- F4: contribuciones de jugadores con estados (pliego F4).
CREATE TABLE IF NOT EXISTS wiki_contribuciones (
    id          SERIAL      PRIMARY KEY,
    pagina_id   INTEGER     NOT NULL REFERENCES wiki_paginas (id) ON DELETE CASCADE,
    mesa_id     TEXT        NOT NULL,
    autor_id    TEXT        NOT NULL,
    autor_nome  TEXT,
    cuerpo      JSONB       NOT NULL,
    estado      TEXT        NOT NULL DEFAULT 'pendiente'
                            CHECK (estado IN ('pendiente', 'aprobada', 'rechazada')),
    revisado_por TEXT,
    revisado_en TIMESTAMPTZ,
    creado_en   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_contribuciones_pagina
    ON wiki_contribuciones (pagina_id, estado);
