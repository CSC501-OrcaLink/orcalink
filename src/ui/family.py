import re

from flask import Blueprint, current_app, redirect, render_template, request, url_for

from src.dal.family import add_whale, list_matrilines, lookup_family, update_matriline


family_bp = Blueprint("family", __name__, template_folder="templates")
SAVE_MESSAGES = {
    "add": "Whale added to the knowledge graph.",
    "update": "Matriline updated in the knowledge graph.",
}


@family_bp.route("/family", methods=["GET", "POST"])
def lookup():
    fields = request.form if request.method == "POST" else request.args
    code = fields.get("code", "").strip().upper()
    results = None
    matrilines = {}
    error = None

    try:
        if request.method == "POST":
            action = request.form.get("action")
            if not re.fullmatch(r"[A-Z][A-Z0-9_-]{0,19}", code):
                raise ValueError("Enter a whale code such as J49 (up to 20 characters).")
            if action == "add":
                add_whale(code)
            elif action == "update":
                update_matriline(code, request.form.get("matriline", ""))
            else:
                raise ValueError("Choose a valid action.")
            return redirect(url_for("family.lookup", code=code, saved=action), code=303)

        if code:
            results = lookup_family(code)
            if results:
                matrilines = list_matrilines()
    except ValueError as exc:
        error = str(exc)
    except OSError:
        current_app.logger.exception("Could not access the semantic store")
        error = "Could not access the knowledge graph. Check that it has been loaded."

    return render_template(
        "family.html",
        code=code,
        results=results,
        matrilines=matrilines,
        error=error,
        message=SAVE_MESSAGES.get(request.args.get("saved")),
    )
