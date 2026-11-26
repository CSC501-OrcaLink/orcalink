-- Link individual observations to sightings and whales
CREATE TABLE IF NOT EXISTS IndividualObservation (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    SightingId INTEGER NOT NULL,
    WhaleId INTEGER,
    OriginalWhaleLabel TEXT,
    IdentificationStatus TEXT,
    IdentificationBasis TEXT,
    SourceRecordId TEXT NOT NULL,
    Notes TEXT,

    CONSTRAINT UK_IndividualObservation_SourceRecordId
        UNIQUE (SourceRecordId),

    CONSTRAINT FK_IndividualObservation_SightingId_2_Sighting_Id
        FOREIGN KEY (SightingId)
        REFERENCES Sighting(Id),

    CONSTRAINT FK_IndividualObservation_WhaleId_2_Whale_Id
        FOREIGN KEY (WhaleId)
        REFERENCES Whale(Id)
);