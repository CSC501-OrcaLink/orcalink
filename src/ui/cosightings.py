from flask import Blueprint, current_app, render_template, request

from src.dal.cosightings import lookup_cosightings

cosightings_bp = Blueprint("cosightings", __name__, template_folder="templates")

@cosightings_bp.get("/cosightings")
def lookup():
    code = request.args.get("code", "").strip().upper()
    results = None
    error = None

    if code:
        try:
            results = lookup_cosightings(code)
        except OSError:
            current_app.logger.exception("Could not read co-sighting data")
            error = "Could not read the co-sighting data. Check that the graph is loaded."

    return render_template("cosightings.html", code=code, results=results, error=error)