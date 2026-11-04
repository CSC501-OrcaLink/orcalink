-- Validate GroupObservation records and their relationships.

-- Total number of group observations.
SELECT COUNT(*) AS GroupObservationCount
FROM GroupObservation;

-- Check for broken foreign-key relationships.
SELECT COUNT(*) AS OrphanGroupObservations
FROM GroupObservation AS G
LEFT JOIN Sighting AS S
    ON G.SightingId = S.Id
WHERE S.Id IS NULL;

-- Check missing group-identification fields.
SELECT
    COUNT(*) AS Total,
    SUM(CASE WHEN ReportedGroup IS NULL THEN 1 ELSE 0 END)
        AS MissingReportedGroup,
    SUM(CASE WHEN LikelyGroup IS NULL THEN 1 ELSE 0 END)
        AS MissingLikelyGroup
FROM GroupObservation;

-- Example join between a sighting and its group-level observation.
SELECT
    S.SourceRecordId,
    S.SightingDate,
    G.ReportedGroup,
    G.LikelyGroup,
    G.IdentificationLevel
FROM GroupObservation AS G
JOIN Sighting AS S
    ON G.SightingId = S.Id
WHERE S.SourceRecordId = 'TWM_0000004';