import os
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Use a temporary database
with tempfile.TemporaryDirectory() as folder:
    db = Path(folder) / "test.db"

    conn = sqlite3.connect(db)
    conn.executescript(
        (ROOT / "sql/01_whale.sql").read_text()
    )
    conn.execute(
        "INSERT INTO Whale (WhaleCode, Name) VALUES (?, ?)",
        ("J1", "Test whale")
    )
    conn.commit()
    conn.close()

    # Connect Flask to the test database
    os.environ["ORCALINK_DB"] = str(db)
    sys.path.insert(0, str(ROOT))

    from app import app

    app.testing = True
    client = app.test_client()

    # View and search
    page = client.get("/?search=J1")
    assert page.status_code == 200
    assert b"J1" in page.data

    # Add a whale
    client.post("/", data={
        "action": "add",
        "code": "TEST_UI",
        "name": "New whale"
    })

    with sqlite3.connect(db) as conn:
        whale_id = conn.execute(
            "SELECT Id FROM Whale WHERE WhaleCode = 'TEST_UI'"
        ).fetchone()[0]

    # Update the whale
    client.post("/", data={
        "action": "edit",
        "id": whale_id,
        "name": "Updated whale"
    })

    with sqlite3.connect(db) as conn:
        name = conn.execute(
            "SELECT Name FROM Whale WHERE Id = ?",
            (whale_id,)
        ).fetchone()[0]

    assert name == "Updated whale"

    # Delete the whale
    client.post("/", data={
        "action": "delete",
        "id": whale_id
    })

    with sqlite3.connect(db) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM Whale WHERE Id = ?",
            (whale_id,)
        ).fetchone()[0]

    assert count == 0

print("Flask tests passed: view, search, add, edit, delete")