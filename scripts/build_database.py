import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "orcalink_demo.db"
DATA = ROOT / "data/processed/data"

FILES = [
    "historical_sightings_all.csv",
    "dryad_sighting_groups.csv",
    "j_lifespans_all.csv",
    "individual_observations_all.csv",
]

EXPECTED = {
    "DataSource": 2,
    "Location": 38926,
    "Sighting": 122764,
    "Whale": 130,
    "ObservationStaging": 35042,
    "IndividualObservation": 35042,
    "GroupObservation": 116822,
    "Association": 686,
}


def run_script(name, db):
    print("Running", name, flush=True)

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / name), str(db)],
        cwd=ROOT,
        check=True,
    )


def run_sql(name, db):
    with sqlite3.connect(db) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript((ROOT / "sql" / name).read_text())


def check_database(db, check_counts=True):
    with sqlite3.connect(db) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        # Check the number of records in each table
        for table, expected in EXPECTED.items():
            count = conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            print(f"{table}: {count:,}")

            # Only require exact counts when building a fresh database
            if check_counts and count != expected:
                raise RuntimeError(
                    f"Wrong row count in {table}: {count}"
                )

        # Check observations without a matching sighting
        unmatched = conn.execute("""
            SELECT COUNT(*)
            FROM ObservationStaging O
            LEFT JOIN Sighting S
                ON O.SightingKey = S.SightingKey
            WHERE S.Id IS NULL
        """).fetchone()[0]

        # Check foreign keys
        errors = conn.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        # Check association values
        bad_pairs = conn.execute("""
            SELECT COUNT(*)
            FROM Association
            WHERE WhaleAId >= WhaleBId
               OR Score NOT BETWEEN 0 AND 1
               OR SharedSightingCount <= 0
               OR WhaleASightingCount < SharedSightingCount
               OR WhaleBSightingCount < SharedSightingCount
        """).fetchone()[0]

        print("Unmatched sightings:", unmatched)
        print("Foreign-key errors:", len(errors))
        print("Invalid associations:", bad_pairs)

        if unmatched or errors or bad_pairs:
            raise RuntimeError("Database checks failed")


def build_database(db):
    # Make sure the CSV files exist
    for name in FILES:
        if not (DATA / name).exists():
            raise FileNotFoundError(
                f"Missing source file: {name}"
            )

    # Load the parent records first
    run_script("import_sightings.py", db)
    run_sql("01_whale.sql", db)
    run_script("load_whales.py", db)

    # Link observations to sightings and whales
    run_script("load_observations.py", db)
    run_script("link_observations.py", db)

    # Load group observations and calculate associations
    run_script("load_group_observations.py", db)
    run_sql("09_association.sql", db)
    run_script("build_associations.py", db)

    check_database(db)


def main():
    if len(sys.argv) > 2 or (
        len(sys.argv) == 2 and sys.argv[1] != "--rebuild"
    ):
        raise SystemExit(
            "Usage: python3 scripts/build_database.py [--rebuild]"
        )

    if DB.exists() and "--rebuild" not in sys.argv:
        print("Using existing orcalink_demo.db")
        check_database(DB, check_counts=False)
        return

    # Build in a temporary folder so the old database stays safe
    with tempfile.TemporaryDirectory(dir=ROOT) as folder:
        new_db = Path(folder) / "orcalink_demo.db"

        build_database(new_db)

        # Replace the demo database only after checks pass
        new_db.replace(DB)

    print("Database ready:", DB)


if __name__ == "__main__":
    main()
