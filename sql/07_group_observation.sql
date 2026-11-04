-- Store group-level identification information for sightings.
-- These records do not imply that individual whales were identified.

CREATE TABLE IF NOT EXISTS GroupObservation (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    SightingId INTEGER NOT NULL,
    ReportedGroup TEXT,
    LikelyGroup TEXT,
    IdentificationLevel TEXT NOT NULL,

    CONSTRAINT FK_GroupObservation_SightingId_2_Sighting_Id
        FOREIGN KEY (SightingId)
        REFERENCES Sighting(Id)
);