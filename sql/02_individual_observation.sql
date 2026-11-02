
-- Link individual observations to sightings and whales.
CREATE TABLE IF NOT EXISTS IndividualObservation (
    observation_id INTEGER PRIMARY KEY,
    sighting_id INTEGER NOT NULL REFERENCES Sighting(sighting_id),
    whale_id INTEGER REFERENCES Whale(whale_id),
    original_whale_label TEXT,
    identification_status TEXT,
    identification_basis TEXT,
    source_record_id TEXT NOT NULL UNIQUE,
    notes TEXT
);
