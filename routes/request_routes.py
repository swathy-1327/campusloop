from flask import Blueprint, flash, redirect, render_template, request, url_for

from models.request_model import create_rent_request, create_unavailable_request, list_requests_for_user
from utils.auth import current_user, login_required

request_bp = Blueprint("request", __name__, url_prefix="/requests")


@request_bp.route("/")
@login_required
def request_center():
    user = current_user()
    return render_template("requests.html", requests_data=list_requests_for_user(str(user["_id"])))


@request_bp.route("/rent", methods=["GET", "POST"])
@login_required
def rent_request():
    if request.method == "POST":
        user = current_user()
        product_name = request.form.get("product_name", "").strip()
        category = request.form.get("category", "").strip()
        duration = request.form.get("duration", "").strip()
        budget = request.form.get("budget", "").strip()
        note = request.form.get("note", "").strip()
        if not all([product_name, category, duration, budget]):
            flash("Please fill in the required rental request fields.", "error")
            return render_template("rent_request.html")

        create_rent_request(str(user["_id"]), product_name, category, duration, float(budget), note)
        flash("Rental request posted.", "success")
        return redirect(url_for("request.request_center"))

    return render_template("rent_request.html")


@request_bp.route("/unavailable", methods=["GET", "POST"])
@login_required
def unavailable_request():
    if request.method == "POST":
        user = current_user()
        product_name = request.form.get("product_name", "").strip()
        category = request.form.get("category", "").strip()
        budget = request.form.get("budget", "").strip()
        description = request.form.get("description", "").strip()
        if not all([product_name, category, budget]):
            flash("Please fill in the required unavailable-item fields.", "error")
            return render_template("unavailable_request.html")

        create_unavailable_request(str(user["_id"]), product_name, category, float(budget), description)
        flash("Unavailable item request posted.", "success")
        return redirect(url_for("request.request_center"))

    return render_template("unavailable_request.html")
