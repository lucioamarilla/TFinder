CREATE TABLE IF NOT EXISTS notificaciones (
    id        SERIAL      PRIMARY KEY,
    grupo     TEXT        NOT NULL DEFAULT 'mesas'
                          CHECK (grupo IN ('mesas', 'social', 'sesiones')),
    icono     TEXT        NOT NULL DEFAULT 'solicitud',
    leida     BOOLEAN     NOT NULL DEFAULT FALSE,
    autor     TEXT,
    mensaje   TEXT        NOT NULL,
    entidad   TEXT,
    detalle   TEXT,
    enlace    JSONB,
    fecha     TEXT,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS event_log (
    id           SERIAL      PRIMARY KEY,
    entidad_tipo TEXT        NOT NULL,
    entidad_id   TEXT,
    accion       TEXT        NOT NULL,
    usuario_id   TEXT,
    metadata     JSONB,
    ocurrido_en  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_event_log_entidad ON event_log (entidad_tipo, entidad_id);