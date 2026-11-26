-- Sighting import checks. Run with:
--   sqlite3 part2_test.db < sql/sighting_checks.sql
.mode box
.headers on

-- 1. Sightings per source
SELECT
    ds.Name AS source,
    COUNT(*) AS sightings
FROM Sighting s
JOIN DataSource ds ON s.DataSourceId = ds.Id
GROUP BY ds.Name;

-- 2. Missing values per source
SELECT
    ds.Name AS source,
    SUM(s.SightingDate IS NULL) AS no_date,
    SUM(s.SightingTime IS NULL) AS no_time,
    SUM(s.LocationId IS NULL) AS no_location
FROM Sighting s
JOIN DataSource ds ON s.DataSourceId = ds.Id
GROUP BY ds.Name;

-- 3. Conflicts, by field
SELECT
    ConflictFields,
    COUNT(*) AS sightings
FROM Sighting
WHERE HasConflict = 1
GROUP BY ConflictFields;

-- 4. Duplicate (source, record ID) pairs (should return no rows)
SELECT
    DataSourceId,
    SourceRecordId,
    COUNT(*) AS n
FROM Sighting
GROUP BY DataSourceId, SourceRecordId
HAVING n > 1;

-- 5. Shifted vs real data
SELECT
    IsShifted,
    COUNT(*) AS sightings
FROM Sighting
GROUP BY IsShifted;

-- 6. Date range per source (Dryad dates are obfuscated, not real)
SELECT
    ds.Name AS source,
    MIN(s.SightingDate) AS earliest,
    MAX(s.SightingDate) AS latest
FROM Sighting s
JOIN DataSource ds ON s.DataSourceId = ds.Id
GROUP BY ds.Name;

-- 7. Locations with out-of-range coordinates (should return no rows)
SELECT
    Id,
    Latitude,
    Longitude
FROM Location
WHERE Latitude NOT BETWEEN -90 AND 90
   OR Longitude NOT BETWEEN -180 AND 180;

-- 8. Broken foreign keys (should return no rows)
PRAGMA foreign_key_check;