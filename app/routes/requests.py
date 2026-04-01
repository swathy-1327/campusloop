from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import RentRequest, UnavailableProductRequest


requests_bp = Blueprint("requests", __name__)


@requests_bp.route("/rent", methods=["GET", "POST"])
@login_required
def rent_request():
    if request.method == "POST":
        rent_request_obj = RentRequest(
            user_id=current_user.id,
            product_name=request.form["product_name"].strip(),
            category=request.form["category"].strip(),
            duration=request.form["duration"].strip(),
            budget=request.form["budget"],
            note=request.form.get("note", "").strip(),
        )
        db.session.add(rent_request_obj)
        db.session.commit()
        flash("Rental request posted.", "success")
        return redirect(url_for("main.index"))

    requests_list = RentRequest.query.order_by(RentRequest.created_at.desc()).all()
    return render_template("requests/rent_request.html", requests_list=requests_list)


@requests_bp.route("/")
@login_required
def request_center():
    requests_data = {
        "rent_requests": RentRequest.query.filter_by(user_id=current_user.id).order_by(RentRequest.created_at.desc()).all(),
        "unavailable_requests": UnavailableProductRequest.query.filter_by(user_id=current_user.id).order_by(
            UnavailableProductRequest.created_at.desc()
        ).all(),
    }
    return render_template("requests/request_center.html", requests_data=requests_data)


@requests_bp.route("/unavailable", methods=["GET", "POST"])
@login_required
def unavailable_request():
    if request.method == "POST":
        unavailable = UnavailableProductRequest(
            user_id=current_user.id,
            product_name=request.form["product_name"].strip(),
            category=request.form["category"].strip(),
            budget=request.form["budget"],
            description=request.form.get("description", "").strip(),
        )
        db.session.add(unavailable)
        db.session.commit()
        flash("Unavailable item request posted.", "success")
        return redirect(url_for("main.index"))

    requests_list = UnavailableProductRequest.query.order_by(
        UnavailableProductRequest.created_at.desc()
    ).all()
    return render_template("requests/unavailable_request.html", requests_list=requests_list)
