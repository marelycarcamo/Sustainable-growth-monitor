-- ============================================
-- SCHEMA: Sustainable Growth Monitor
-- Base de datos: technova.duckdb
-- ============================================

CREATE TABLE IF NOT EXISTS dim_tiempo (
    id_tiempo INTEGER PRIMARY KEY,
    fecha DATE NOT NULL,
    anio INTEGER,
    mes INTEGER,
    dia INTEGER,
    trimestre INTEGER,
    semana INTEGER,
    nombre_mes VARCHAR,
    dia_semana VARCHAR,
    es_finde BOOLEAN
);

CREATE TABLE IF NOT EXISTS dim_area (
    id_area INTEGER PRIMARY KEY,
    nombre_area VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_metrica (
    id_metrica INTEGER PRIMARY KEY,
    nombre VARCHAR NOT NULL,
    categoria VARCHAR,
    subcategoria VARCHAR,
    unidad VARCHAR,
    formula TEXT,
    prioridad VARCHAR(10),
    frecuencia_recomendada VARCHAR(15),
    tipo_agregacion VARCHAR(10) CHECK (tipo_agregacion IN ('SUM','AVG','LAST')),
    tendencia_deseada VARCHAR(5) CHECK (tendencia_deseada IN ('UP','DOWN')),
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS dim_objetivo (
    id_objetivo INTEGER PRIMARY KEY,
    id_metrica INTEGER NOT NULL,
    anio INTEGER NOT NULL,
    valor_objetivo FLOAT,
    umbral_verde FLOAT,
    umbral_amarillo FLOAT,
    peso_relativo FLOAT,
    FOREIGN KEY (id_metrica) REFERENCES dim_metrica(id_metrica),
    UNIQUE(id_metrica, anio)
);

CREATE TABLE IF NOT EXISTS dim_categoria (
    id_categoria INTEGER PRIMARY KEY,
    nombre_categoria VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_monitoreo (
    id_monitoreo INTEGER PRIMARY KEY,
    id_tiempo INTEGER NOT NULL,
    id_metrica INTEGER NOT NULL,
    id_area INTEGER NOT NULL,
    valor DOUBLE,
    fuente VARCHAR,
    FOREIGN KEY (id_tiempo) REFERENCES dim_tiempo(id_tiempo),
    FOREIGN KEY (id_metrica) REFERENCES dim_metrica(id_metrica),
    FOREIGN KEY (id_area) REFERENCES dim_area(id_area)
);

CREATE TABLE IF NOT EXISTS dim_empleado (
    id_empleado VARCHAR PRIMARY KEY,
    nombre VARCHAR,
    area VARCHAR,
    genero VARCHAR,
    fecha_ingreso DATE
);

CREATE TABLE IF NOT EXISTS dim_proveedor (
    id_proveedor INTEGER PRIMARY KEY,
    nombre_proveedor VARCHAR NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_fact_tiempo ON fact_monitoreo(id_tiempo);
CREATE INDEX IF NOT EXISTS idx_fact_metrica ON fact_monitoreo(id_metrica);
CREATE INDEX IF NOT EXISTS idx_fact_area ON fact_monitoreo(id_area);
CREATE INDEX IF NOT EXISTS idx_objetivo_anio ON dim_objetivo(anio);

