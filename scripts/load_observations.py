
import csv
import sqlite3
from pathlib import Path

# Get the main OrcaLink project folder.
project_dir = Path(__file__).resolve().parent.parent

# Paths to the database and observation dataset.
db_path = project_dir / "orcalink.db"
csv_path = project_dir / "data/processed/data/individual_observations_all.csv"

# Connect to SQLite.
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA foreign_keys = ON")

# Create a staging table for the CSV data.
# We will link these records to Sighting later.
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

# Read the preprocessed CSV.
with open(csv_path, newline="", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)

    # Refresh the staging data when the script runs again.
    conn.execute("DELETE FROM ObservationStaging")

    for row in reader:

        # Insert one observation from the CSV.
        conn.execute("""
            INSERT INTO ObservationStaging (
                source_record_id
                original_whale_label
                whale_code
                id_category
                source_sighting_id
                sighting_key
                observation_time
                identification_status
                identification_basis
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

# Save the records.
conn.commit()

# Count the imported observations.
count = conn.execute(
    "SELECT COUNT(*) FROM ObservationStaging"
).fetchone()[0]

print(f"Total observations loaded: {count}")

# Close the database.
conn.close()
