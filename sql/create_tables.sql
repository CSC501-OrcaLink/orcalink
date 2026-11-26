PRAGMA foreign_keys = ON;

CREATE TABLE DataSource (
    Id          INTEGER PRIMARY KEY AUTOINCREMENT,
    Name        TEXT NOT NULL,
    Description TEXT,
    Url         TEXT,

    CONSTRAINT UK_DataSource_Name UNIQUE (Name)
);

CREATE TABLE Location (
    Id                INTEGER PRIMARY KEY AUTOINCREMENT,
    FishArea          TEXT,
    Quadrant          TEXT,
    Latitude          REAL,
    Longitude         REAL,
    AlternateLatitude REAL,
    AlternateLongitude REAL,
    UtmX              REAL,
    UtmY              REAL,
    DryadXKm          REAL,
    DryadYKm          REAL,
    CHECK (Latitude IS NULL OR Latitude BETWEEN -90 AND 90),
    CHECK (Longitude IS NULL OR Longitude BETWEEN -180 AND 180),
    CHECK (AlternateLatitude IS NULL OR AlternateLatitude BETWEEN -90 AND 90),
    CHECK (AlternateLongitude IS NULL OR AlternateLongitude BETWEEN -180 AND 180)
);

CREATE TABLE Sighting (
    Id               INTEGER PRIMARY KEY AUTOINCREMENT,
    SightingKey      TEXT NOT NULL,
    DataSourceId     INTEGER NOT NULL,
    SourceRecordId   TEXT NOT NULL,
    SourceDetail     TEXT,
    SourceFile       TEXT,
    SourceRow        INTEGER,
    SightingDate     TEXT,
    SightingTime     TEXT,
    TimeZone         TEXT,
    IsShifted        INTEGER NOT NULL DEFAULT 0 CHECK (IsShifted IN (0,1)),
    DateParseFailed  INTEGER NOT NULL DEFAULT 0 CHECK (DateParseFailed IN (0,1)),
    TimeParseFailed  INTEGER NOT NULL DEFAULT 0 CHECK (TimeParseFailed IN (0,1)),
    LocationId       INTEGER,
    ObsMethods       TEXT,
    HasConflict      INTEGER NOT NULL DEFAULT 0 CHECK (HasConflict IN (0,1)),
    ConflictFields   TEXT,
    CONSTRAINT UK_Sighting_SightingKey UNIQUE (SightingKey),
    CONSTRAINT UK_Sighting_DataSourceId_SourceRecordId
        UNIQUE (DataSourceId, SourceRecordId),

    CONSTRAINT FK_Sighting_DataSourceId_2_DataSource_Id
        FOREIGN KEY (DataSourceId)
        REFERENCES DataSource(Id),

    CONSTRAINT FK_Sighting_LocationId_2_Location_Id
        FOREIGN KEY (LocationId)
        REFERENCES Location(Id)
);