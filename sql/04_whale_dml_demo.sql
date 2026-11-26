
-- Test adding, changing and deleting a whale.
BEGIN TRANSACTION;

-- Add a temporary whale.
INSERT INTO Whale (WhaleCode, Notes)
VALUES ('TEST_M4', 'Temporary test whale');

SELECT * FROM Whale WHERE WhaleCode = 'TEST_M4';

-- Update the test whale.
UPDATE Whale
SET Notes = 'Updated test record'
WHERE WhaleCode = 'TEST_M4';

SELECT * FROM Whale WHERE WhaleCode = 'TEST_M4';

-- Delete the test whale.
DELETE FROM Whale WHERE WhaleCode = 'TEST_M4';

SELECT COUNT(*) FROM Whale WHERE WhaleCode = 'TEST_M4';

-- Undo the test changes.
ROLLBACK;

-- Confirm the original records remain.
SELECT COUNT(*) FROM Whale;
