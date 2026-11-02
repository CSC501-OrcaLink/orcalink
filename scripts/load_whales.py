
import csv
import sqlite3
from pathlib import Path

# File locations
root = Path(__file__).resolve().parent.parent
csv_path = root / "data/processed/data/j_lifespans_all.csv"
db_path = root / "orcalink.db"

# Open the database
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA foreign_keys = ON")

# Read and insert whale records
with open(csv_path, newline="", encoding="utf-8-sig") as file:
    for row in csv.DictReader(file):
        code = row["whale_id"].strip()

        if not code:
            continue

        birth = row["birth_date"] or None
        death = row["death_datetime"][:10] or None

        # Add a whale, or update its dates if it exists
        conn.execute("""
            INSERT INTO Whale (whale_code, birth_date, death_date)
            VALUES (?, ?, ?)
            ON CONFLICT(whale_code) DO UPDATE SET
                birth_date = excluded.birth_date,
                death_date = excluded.death_date
        """, (code, birth, death))

# Save and check the results
conn.commit()
count = conn.execute("SELECT COUNT(*) FROM Whale").fetchone()[0]
print("Total whales:", count)

conn.close()