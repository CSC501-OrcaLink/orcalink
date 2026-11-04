-- Link individual observations to sightings and whales
CREATE TABLE IF NOT EXISTS IndividualObservation (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    SightingId INTEGER NOT NULL,
    WhaleId INTEGER,
    OriginalWhaleLabel TEXT,
    IdentificationStatus TEXT,
    IdentificationBasis TEXT,
    SourceRecordId TEXT NOT NULL UNIQUE,
    Notes TEXT,
    FOREIGN KEY (SightingId) REFERENCES Sighting(Id),
    FOREIGN KEY (WhaleId) REFERENCES Whale(Id)
);