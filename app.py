
import sqlite3
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for

# Set up Flask and the database.
app = Flask(__name__, static_folder="assets", static_url_path="/assets")
DB = Path(__file__).with_name("orcalink.db")

def open_db():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

@app.route("/", methods=["GET", "POST"])
def home():
    db = open_db()

    # Add, edit, or delete a whale.
    if request.method == "POST":
        action = request.form.get("action")
        whale_id = request.form.get("id")
        code = request.form.get("code", "").strip().upper()

        # Convert empty fields to NULL.
        def field(name):
            return request.form.get(name, "").strip() or None

        details = (
            field("name"),
            field("sex"),
            field("birth"),
            field("death"),
            field("notes")
        )

        try:
            if action == "add" and code:
                db.execute("""
                    INSERT INTO Whale
                    (whale_code, name, sex, birth_date, death_date, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (code, *details))
                message = "Whale added."

            elif action == "edit":
                db.execute("""
                    UPDATE Whale
                    SET name = ?, sex = ?, birth_date = ?,
                        death_date = ?, notes = ?
                    WHERE whale_id = ?
                """, (*details, whale_id))
                message = "Whale updated."

            elif action == "delete":
                db.execute(
                    "DELETE FROM Whale WHERE whale_id = ?",
                    (whale_id,)
                )
                message = "Whale deleted."

            else:
                message = "A whale code is required."

            db.commit()

        except sqlite3.IntegrityError as e:
            db.rollback()
            message = f"Could not save: {e}"

        db.close()
        return redirect(url_for("home", message=message))

    # Search whales and display 20 per page.
    search = request.args.get("search", "").strip()
    page = max(1, request.args.get("page", 1, type=int) or 1)
    per_page = 20

    where = ""
    values = []

    if search:
        where = " WHERE whale_code LIKE ? OR name LIKE ?"
        values = [f"%{search}%", f"%{search}%"]

    # Count the matching whales.
    total = db.execute(
        "SELECT COUNT(*) FROM Whale" + where, values
    ).fetchone()[0]

    last_page = max(1, (total + per_page - 1) // per_page)
    page = min(page, last_page)

    # Get the records for the current page.
    whales = db.execute(
        "SELECT * FROM Whale" + where +
        " ORDER BY whale_code LIMIT ? OFFSET ?",
        (*values, per_page, (page - 1) * per_page)
    ).fetchall()

    db.close()

    return render_template(
        "index.html",
        whales=whales,
        search=search,
        total=total,
        page=page,
        last_page=last_page,
        message=request.args.get("message", "")
    )

if __name__ == "__main__":
    app.run(debug=True)
