-- ==========================================
-- OrcaLink - Whale and Observation Queries
-- ==========================================

-- Query 1: Show the first 10 whales.
-- This checks the whale information stored in our database.

SELECT Id, WhaleCode, BirthDate, DeathDate
FROM Whale
ORDER BY Id
LIMIT 10;

-- Query 2: Find observations associated with J1.
-- JOIN connects Whale and ObservationStaging
-- using their matching whale identification codes.

SELECT
    w.WhaleCode,
    o.SourceRecordId,
    o.SightingKey,
    o.ObservationTime
FROM Whale AS w
JOIN ObservationStaging AS o
    ON w.WhaleCode = o.WhaleCode
WHERE w.WhaleCode = 'J1'
LIMIT 10;

-- Query 3: Count observations for each known whale.
-- GROUP BY puts observations of the same whale together.
-- COUNT counts the number of records in each group.

SELECT
    w.WhaleCode,
    COUNT(o.SourceRecordId) AS TotalObservations
FROM Whale AS w
JOIN ObservationStaging AS o
    ON w.WhaleCode = o.WhaleCode
GROUP BY w.Id, w.WhaleCode
ORDER BY TotalObservations DESC
LIMIT 10;

-- Query 4: Count observations by identification category.
-- This includes observations with missing or unresolved IDs.

SELECT
    IdCategory,
    COUNT(*) AS Total
FROM ObservationStaging
GROUP BY IdCategory;