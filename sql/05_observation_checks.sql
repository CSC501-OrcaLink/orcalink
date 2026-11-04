-- Count all observations.
SELECT COUNT(*) FROM ObservationStaging;

-- Count different sightings.
SELECT COUNT(DISTINCT SightingKey)
FROM ObservationStaging;

-- Check observations without a sighting key.
SELECT COUNT(*)
FROM ObservationStaging
WHERE SightingKey IS NULL;

-- Check whether the Sighting table exists.
SELECT name FROM sqlite_master
WHERE name = 'Sighting' AND type = 'table';

-- Check the observation foreign keys.
PRAGMA foreign_key_list(IndividualObservation);
