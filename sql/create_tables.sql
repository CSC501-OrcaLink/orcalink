PRAGMA foreign_keys = ON;

CREATE TABLE DataSource (
    source_id    INTEGER PRIMARY KEY,
    name         TEXT NOT NULL UNIQUE,
    description  TEXT,
    url          TEXT
);

CREATE TABLE Location (
    location_id         INTEGER PRIMARY KEY,
    fish_area           TEXT,
    quadrant            TEXT,
    latitude            REAL,
    longitude           REAL,
    alternate_latitude  REAL,
    alternate_longitude REAL,
    utm_x               REAL,
    utm_y               REAL,
    dryad_x_km          REAL,
    dryad_y_km          REAL,
    CHECK (latitude  IS NULL OR latitude  BETWEEN -90  AND 90),
    CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180),
    CHECK (alternate_latitude  IS NULL OR alternate_latitude  BETWEEN -90  AND 90),
    CHECK (alternate_longitude IS NULL OR alternate_longitude BETWEEN -180 AND 180)
);

CREATE TABLE Sighting (
    sighting_id       INTEGER PRIMARY KEY,
    sighting_key      TEXT NOT NULL UNIQUE,
    source_id         INTEGER NOT NULL REFERENCES DataSource(source_id),
    source_record_id  TEXT NOT NULL,
    source_detail     TEXT,
    source_file       TEXT,
    source_row        INTEGER,
    sighting_date     TEXT,
    sighting_time     TEXT,
    time_zone         TEXT,
    is_shifted        INTEGER NOT NULL DEFAULT 0 CHECK (is_shifted IN (0,1)),
    date_parse_failed INTEGER NOT NULL DEFAULT 0 CHECK (date_parse_failed IN (0,1)),
    time_parse_failed INTEGER NOT NULL DEFAULT 0 CHECK (time_parse_failed IN (0,1)),
    location_id       INTEGER REFERENCES Location(location_id),
    obs_methods       TEXT,
    has_conflict      INTEGER NOT NULL DEFAULT 0 CHECK (has_conflict IN (0,1)),
    conflict_fields   TEXT,
    UNIQUE (source_id, source_record_id)
);