import csv
import sqlite3
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
csv_path = root / "data/processed/data/individual_observations_all.csv"
db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "orcalink.db"

conn = sqlite3.connect(db_path)
conn.execute("PRAGMA foreign_keys = ON")

# Store the original observations before linking them
conn.execute("""
    CREATE TABLE IF NOT EXISTS ObservationStaging (
        SourceRecordId TEXT PRIMARY KEY,
        OriginalWhaleLabel TEXT,
        WhaleCode TEXT,
        IdCategory TEXT,
        SourceSightingId TEXT,
        SightingKey TEXT,
        ObservationTime TEXT,
        IdentificationStatus TEXT,
        IdentificationBasis TEXT
    )
""")

with open(csv_path, newline="", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)

    with conn:
        conn.execute("DELETE FROM ObservationStaging")

        for row in reader:
            conn.execute("""
                INSERT INTO ObservationStaging (
                    SourceRecordId, OriginalWhaleLabel, WhaleCode,
                    IdCategory, SourceSightingId, SightingKey,
                    ObservationTime, IdentificationStatus,
                    IdentificationBasis
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["record_id"],
                row["ID"],
                row["whale_id"] or None,
                row["id_category"],
                row["source_sighting_id"] or None,
                row["sighting_key"] or None,
                row["datetime_utc_shifted"] or None,
                row["identification_status"] or None,
                row["identification_basis"] or None
            ))

count = conn.execute(
    "SELECT COUNT(*) FROM ObservationStaging"
).fetchone()[0]

print("Staged observations:", count)
conn.close()