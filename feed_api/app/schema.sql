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