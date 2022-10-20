CREATE TABLE IF NOT EXISTS deposits(
    id SERIAL PRIMARY KEY,
    area_name TEXT NOT NULL CHECK (area_name != '') UNIQUE
);

CREATE TABLE IF NOT EXISTS works(
    id SERIAL PRIMARY KEY,
    well_name TEXT,
    start_time TIMESTAMP NOT NULL,
    work_type TEXT NOT NULL,
    deposit_id INTEGER NOT NULL,
    FOREIGN KEY(deposit_id) REFERENCES deposits(id)
);

CREATE TABLE IF NOT EXISTS stations(
    id SERIAL PRIMARY KEY,
    x_wgs84 INTEGER NOT NULL,
    y_wgs84 INTEGER NOT NULL,
    altitude INTEGER NOT NULL,
    work_id INTEGER NOT NULL,
    FOREIGN KEY(work_id) REFERENCES works(id)
);

CREATE TABLE IF NOT EXISTS seismic_records(
    id SERIAL PRIMARY KEY,
    start_time TIMESTAMP NOT NULL,
    stop_time TIMESTAMP NOT NULL,
    frequency INTEGER NOT NULL,
    is_using BOOLEAN NOT NULL,
    origin_name TEXT NOT NULL,
    unique_name TEXT NOT NULL UNIQUE,
    station_id INTEGER NOT NULL,
    FOREIGN KEY(station_id) REFERENCES stations(id)
);
