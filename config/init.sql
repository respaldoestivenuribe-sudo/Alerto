-- ── Bronze layer ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bronze_weather_current (
    id                SERIAL PRIMARY KEY,
    fetched_at        TIMESTAMPTZ NOT NULL,
    time              TIMESTAMPTZ NOT NULL,
    precipitation     FLOAT,
    rain              FLOAT,
    showers           FLOAT,
    relative_humidity FLOAT,
    cloudcover        FLOAT,
    windspeed_10m     FLOAT
);

CREATE TABLE IF NOT EXISTS bronze_weather_hourly (
    id                SERIAL PRIMARY KEY,
    fetched_at        TIMESTAMPTZ NOT NULL,
    time              TIMESTAMPTZ UNIQUE NOT NULL,
    precipitation     FLOAT,
    rain              FLOAT,
    showers           FLOAT,
    relative_humidity FLOAT,
    cloudcover        FLOAT,
    windspeed_10m     FLOAT
);

-- ── Alerts ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS alerts (
    id                SERIAL PRIMARY KEY,
    evaluated_at      TIMESTAMPTZ NOT NULL,
    precip_1h         FLOAT NOT NULL,
    precip_3h         FLOAT NOT NULL,
    intensidad_actual FLOAT NOT NULL,
    humedad_prom_6h   FLOAT NOT NULL,
    nivel_lluvia      FLOAT NOT NULL,
    riesgo_score      FLOAT NOT NULL,
    nivel_riesgo      VARCHAR(10) NOT NULL
);

-- ── Users (RF-014, RF-015) ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id                SERIAL PRIMARY KEY,
    nombre            VARCHAR(100) NOT NULL,
    email             VARCHAR(255) UNIQUE NOT NULL,
    password_hash     VARCHAR(255) NOT NULL,
    security_question VARCHAR(500) NOT NULL,
    security_answer   VARCHAR(255) NOT NULL,
    role              VARCHAR(20)  NOT NULL DEFAULT 'usuario',
    is_active         BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ── Audit log (RNF-SEG-003) ───────────────────────────────────────────────────
-- Append-only: no DELETE or UPDATE should ever be issued against this table.
CREATE TABLE IF NOT EXISTS audit_log (
    id          SERIAL PRIMARY KEY,
    ts          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    user_email  VARCHAR(255),
    action      VARCHAR(100) NOT NULL,
    resource    VARCHAR(100),
    result      VARCHAR(20)  NOT NULL,
    ip_address  VARCHAR(45),
    details     TEXT
);

-- ── System configuration (RF-005, RF-006) ────────────────────────────────────
CREATE TABLE IF NOT EXISTS system_config (
    key         VARCHAR(100) PRIMARY KEY,
    value       VARCHAR(500) NOT NULL,
    description VARCHAR(500),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_by  VARCHAR(255)
);

INSERT INTO system_config (key, value, description) VALUES
    ('threshold_amarillo', '25', 'Score mínimo para nivel AMARILLO (0-100)'),
    ('threshold_naranja',  '50', 'Score mínimo para nivel NARANJA (0-100)'),
    ('threshold_rojo',     '75', 'Score mínimo para nivel ROJO (0-100)'),
    ('pipeline_interval',  '15', 'Frecuencia de ejecución del pipeline en minutos')
ON CONFLICT (key) DO NOTHING;
