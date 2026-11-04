import csv
import sqlite3
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
csv_path = root / "data/processed/data/j_lifespans_all.csv"
db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "orcalink.db"

# Load the prepared whale records
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA foreign_keys = ON")

with open(csv_path, newline="", encoding="utf-8-sig") as file:
    for row in csv.DictReader(file):
        code = row["whale_id"].strip()

        if not code:
            continue

        birth = row["birth_date"].strip() or None
        death = row["death_datetime"].strip()[:10] or None

        conn.execute("""
            INSERT INTO Whale (WhaleCode, BirthDate, DeathDate)
            VALUES (?, ?, ?)
            ON CONFLICT(WhaleCode) DO UPDATE SET
                BirthDate = excluded.BirthDate,
                DeathDate = excluded.DeathDate
        """, (code, birth, death))

conn.commit()

count = conn.execute("SELECT COUNT(*) FROM Whale").fetchone()[0]
print("Total whales:", count)

conn.close()