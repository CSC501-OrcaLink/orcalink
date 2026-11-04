-- Validate derived co-sighting associations.

-- Total number of associations.
SELECT COUNT(*) AS AssociationCount
FROM Association;

-- Check that all whale foreign keys resolve.
SELECT COUNT(*) AS OrphanAssociations
FROM Association AS A
LEFT JOIN Whale AS WA
    ON A.WhaleAId = WA.Id
LEFT JOIN Whale AS WB
    ON A.WhaleBId = WB.Id
WHERE WA.Id IS NULL
   OR WB.Id IS NULL;

-- Check canonical whale-pair ordering.
SELECT COUNT(*) AS InvalidPairOrder
FROM Association
WHERE WhaleAId >= WhaleBId;

-- Check score range.
SELECT COUNT(*) AS InvalidScores
FROM Association
WHERE Score < 0.0
   OR Score > 1.0;

-- Show associations with whale codes.
SELECT
    WA.WhaleCode AS WhaleA,
    WB.WhaleCode AS WhaleB,
    A.SharedSightingCount,
    A.WhaleASightingCount,
    A.WhaleBSightingCount,
    ROUND(A.Score, 3) AS Score,
    A.Method,
    A.EvidencePolicy
FROM Association AS A
JOIN Whale AS WA
    ON A.WhaleAId = WA.Id
JOIN Whale AS WB
    ON A.WhaleBId = WB.Id
ORDER BY A.Score DESC, A.SharedSightingCount DESC
LIMIT 20;