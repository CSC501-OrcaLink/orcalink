import csv
import sqlite3
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_DIR / "data/processed/data/historical_sightings_all.csv"
SCHEMA_PATH = PROJECT_DIR / "sql/07_group_observation.sql"

DB_PATH = (
    Path(sys.argv[1])
    if len(sys.argv) > 1
    else PROJECT_DIR / "orcalink.db"
)


def clean(value):
    if value is None:
        return None

    value = value.strip()

    if value in ("", "NA", "N/A", "not supplied"):
        return None

    return value


def to_bool(value):
    value = clean(value)
    return value is not None and value.lower() == "true"


def table_exists(conn, table_name):
    return conn.execute("""
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
    """, (table_name,)).fetchone() is not None


def load_group_observations(conn):

    # Load all TWM sighting IDs into memory once.
    sighting_lookup = {
        source_record_id: sighting_id
        for sighting_id, source_record_id in conn.execute("""
            SELECT Sighting.Id, Sighting.SourceRecordId
            FROM Sighting
            JOIN DataSource
                ON Sighting.DataSourceId = DataSource.Id
            WHERE DataSource.Name = 'TWM'
        """)
    }

    # Load existing records once so repeated runs remain safe.
    existing = {
        (
            sighting_id,
            reported_group or "",
            likely_group or "",
            identification_level or ""
        )
        for sighting_id, reported_group, likely_group, identification_level
        in conn.execute("""
            SELECT
                SightingId,
                ReportedGroup,
                LikelyGroup,
                IdentificationLevel
            FROM GroupObservation
        """)
    }

    rows_to_insert = []

    duplicate_rows_skipped = 0
    no_group_skipped = 0
    unmatched_sightings = 0
    already_loaded = 0

    with open(CSV_PATH, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:

            if to_bool(row["exact_duplicate_of_earlier_row"]):
                duplicate_rows_skipped += 1
                continue

            reported_group = clean(row["reported_group"])
            likely_group = clean(row["likely_group"])
            identification_level = clean(row["identification_level"])

            if reported_group is None and likely_group is None:
                no_group_skipped += 1
                continue

            sighting_id = sighting_lookup.get(row["record_id"])

            if sighting_id is None:
                unmatched_sightings += 1
                continue

            key = (
                sighting_id,
                reported_group or "",
                likely_group or "",
                identification_level or ""
            )

            if key in existing:
                already_loaded += 1
                continue

            rows_to_insert.append((
                sighting_id,
                reported_group,
                likely_group,
                identification_level
            ))

            existing.add(key)

    conn.executemany("""
        INSERT INTO GroupObservation (
            SightingId,
            ReportedGroup,
            LikelyGroup,
            IdentificationLevel
        )
        VALUES (?, ?, ?, ?)
    """, rows_to_insert)

    conn.commit()

    print(f"Group observations inserted: {len(rows_to_insert)}")
    print(f"Exact duplicate source rows skipped: {duplicate_rows_skipped}")
    print(f"Rows without group information skipped: {no_group_skipped}")
    print(f"Unmatched sightings: {unmatched_sightings}")
    print(f"Already loaded: {already_loaded}")


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    # Check dependencies before changing this database.
    for table in ("Sighting", "DataSource"):
        if not table_exists(conn, table):
            conn.close()
            raise RuntimeError(
                f"Required table {table} does not exist. "
                "Load the sighting module first."
            )

    # Only after dependencies are confirmed, create our table.
    with open(SCHEMA_PATH, encoding="utf-8") as file:
        conn.executescript(file.read())

    load_group_observations(conn)

    conn.close()


if __name__ == "__main__":
    main()