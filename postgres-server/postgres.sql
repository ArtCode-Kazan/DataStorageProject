CREATE TABLE IF NOT EXISTS deposits(
    id SERIAL PRIMARY KEY,
    area_name VARCHAR(100) NOT NULL CHECK (area_name != '') UNIQUE
);

CREATE TABLE IF NOT EXISTS works(
    id SERIAL PRIMARY KEY,
    well_name VARCHAR(10) DEFAULT 'NULL',
    start_time TIMESTAMP NOT NULL,
    work_type VARCHAR(20) NOT NULL,
    deposit_id INTEGER NOT NULL,
    FOREIGN KEY(deposit_id) REFERENCES deposits(id) ON DELETE CASCADE,
    CONSTRAINT unique_fields UNIQUE (well_name,
                                     start_time,
                                     work_type,
                                     deposit_id)
);

CREATE TABLE IF NOT EXISTS stations(
    id SERIAL PRIMARY KEY,
    station_number INTEGER NOT NULL,
    x_wgs84 NUMERIC(8, 6) NOT NULL,
    y_wgs84 NUMERIC(8, 6) NOT NULL,
    altitude NUMERIC(6, 1) NOT NULL,
    work_id INTEGER NOT NULL,
    FOREIGN KEY(work_id) REFERENCES works(id) ON DELETE CASCADE,
    CONSTRAINT unique_station_fields UNIQUE (station_number, work_id)
);

CREATE TABLE IF NOT EXISTS seismic_records(
    id SERIAL PRIMARY KEY,
    start_time TIMESTAMP NOT NULL,
    stop_time TIMESTAMP NOT NULL,
    frequency INTEGER NOT NULL,
    is_using BOOLEAN NOT NULL DEFAULT TRUE,
    origin_name TEXT NOT NULL,
    unique_name TEXT NOT NULL UNIQUE,
    station_id INTEGER NOT NULL,
    FOREIGN KEY(station_id) REFERENCES stations(id) ON DELETE CASCADE
);
