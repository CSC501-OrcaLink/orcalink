
-- Whale Constraint Tests

BEGIN TRANSACTION;

-- Test 1: Add a whale without providing an Id.
-- SQLite should generate the Id automatically.
INSERT INTO Whale (WhaleCode)
VALUES ('TEST_WHALE');

SELECT Id, WhaleCode
FROM Whale
WHERE WhaleCode = 'TEST_WHALE';


-- Test 2: Try adding an existing whale code.
-- Expected: UNIQUE constraint error.
INSERT INTO Whale (WhaleCode)
VALUES ('J1');


-- Test 3: Try adding a whale without a code.
-- Expected: NOT NULL constraint error.
INSERT INTO Whale (WhaleCode)
VALUES (NULL);


-- Test 4: Try using an existing primary key.
-- Expected: PRIMARY KEY constraint error.
INSERT INTO Whale (Id, WhaleCode)
VALUES (1, 'TEST_DUP_ID');


-- Undo all successful test changes.
ROLLBACK;

-- Check that the original 130 whales remain.
SELECT COUNT(*) AS TotalWhales
FROM Whale;
