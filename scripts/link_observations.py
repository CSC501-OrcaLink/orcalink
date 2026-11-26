import sqlite3
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "orcalink.db"
schema_path = root / "sql/02_individual_observation.sql"

conn = sqlite3.connect(db_path)
conn.execute("PRAGMA foreign_keys = ON")

# Check that the required tables exist
for table in ("Whale", "Sighting", "ObservationStaging"):
    exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,)
    ).fetchone()

    if not exists:
        conn.close()
        raise RuntimeError(f"Missing table: {table}")

with open(schema_path, encoding="utf-8") as file:
    conn.executescript(file.read())

# Check for observations without a matching sighting
missing = conn.execute("""
    SELECT COUNT(*)
    FROM ObservationStaging AS O
    LEFT JOIN Sighting AS S ON O.SightingKey = S.SightingKey
    WHERE S.Id IS NULL
""").fetchone()[0]

print("Unmatched sightings:", missing)

if missing:
    conn.close()
    raise RuntimeError("Fix unmatched sighting keys before importing")

# Link observations using actual database IDs
with conn:
    conn.execute("""
        INSERT INTO IndividualObservation (
            SightingId, WhaleId, OriginalWhaleLabel,
            IdentificationStatus, IdentificationBasis, SourceRecordId
        )
        SELECT
            S.Id, W.Id, O.OriginalWhaleLabel,
            O.IdentificationStatus, O.IdentificationBasis,
            O.SourceRecordId
        FROM ObservationStaging AS O
        JOIN Sighting AS S ON O.SightingKey = S.SightingKey
        LEFT JOIN Whale AS W ON O.WhaleCode = W.WhaleCode
        WHERE 1
        ON CONFLICT(SourceRecordId) DO UPDATE SET
            SightingId = excluded.SightingId,
            WhaleId = excluded.WhaleId,
            OriginalWhaleLabel = excluded.OriginalWhaleLabel,
            IdentificationStatus = excluded.IdentificationStatus,
            IdentificationBasis = excluded.IdentificationBasis
    """)

count = conn.execute(
    "SELECT COUNT(*) FROM IndividualObservation"
).fetchone()[0]

errors = conn.execute("PRAGMA foreign_key_check").fetchall()

print("Linked observations:", count)
print("Foreign key errors:", len(errors))

conn.close()

if errors:
    raise RuntimeError("Foreign key check failed")