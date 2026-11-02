-- Sighting import checks. Run with:
--   sqlite3 orcalink.db < sql/sighting_checks.sql
.mode box
.headers on

-- 1. Sightings per source
SELECT ds.name AS source, COUNT(*) AS sightings
FROM Sighting s JOIN DataSource ds USING (source_id)
GROUP BY ds.name;

-- 2. Missing values per source
SELECT ds.name AS source,
       SUM(s.sighting_date IS NULL) AS no_date,
       SUM(s.sighting_time IS NULL) AS no_time,
       SUM(s.location_id  IS NULL) AS no_location
FROM Sighting s JOIN DataSource ds USING (source_id)
GROUP BY ds.name;

-- 3. Conflicts, by field
SELECT conflict_fields, COUNT(*) AS sightings
FROM Sighting WHERE has_conflict = 1
GROUP BY conflict_fields;

-- 4. Duplicate (source, record ID) pairs (should return no rows)
SELECT source_id, source_record_id, COUNT(*) AS n
FROM Sighting GROUP BY source_id, source_record_id HAVING n > 1;

-- 5. Shifted vs real data
SELECT is_shifted, COUNT(*) AS sightings FROM Sighting GROUP BY is_shifted;

-- 6. Date range per source (Dryad dates are obfuscated, not real)
SELECT ds.name AS source, MIN(s.sighting_date) AS earliest, MAX(s.sighting_date) AS latest
FROM Sighting s JOIN DataSource ds USING (source_id)
GROUP BY ds.name;

-- 7. Locations with out-of-range coordinates (should return no rows)
SELECT location_id, latitude, longitude FROM Location
WHERE latitude NOT BETWEEN -90 AND 90 OR longitude NOT BETWEEN -180 AND 180;

-- 8. Broken foreign keys (should return no rows)
PRAGMA foreign_key_check;