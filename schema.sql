CREATE TABLE IF NOT EXISTS mesas (
    id              INTEGER   PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT      NOT NULL,
    sistema         TEXT      NOT NULL,
    descripcion     TEXT      NULL,
    tono            TEXT      NULL,
    horario         TEXT      NULL,
    estado          TEXT      NOT NULL DEFAULT 'abierta'
                              CHECK (estado IN ('abierta', 'cerrada')),
    nivel_inicial   INTEGER   NULL,
    jugadores_max   INTEGER   NULL,
    fecha_creacion  DATETIME  DEFAULT CURRENT_TIMESTAMP
);