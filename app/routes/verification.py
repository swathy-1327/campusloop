from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import VerificationRequest


verification_bp = Blueprint("verification", __name__)


@verification_bp.route("/become-seller", methods=["GET", "POST"])
@login_required
def become_seller():
    if request.method == "POST":
        existing = VerificationRequest.query.filter_by(
            user_id=current_user.id,
            status="pending",
        ).first()
        if existing:
            flash("You already have a pending verification request.", "warning")
            return redirect(url_for("verification.become_seller"))

        verification_request = VerificationRequest(
            user_id=current_user.id,
            id_type=request.form["id_type"].strip(),
            id_document_ref=request.form["id_document_ref"].strip(),
            status="pending",
        )
        db.session.add(verification_request)
        db.session.commit()
        flash("Verification request submitted.", "success")
        return redirect(url_for("main.index"))

    my_requests = VerificationRequest.query.filter_by(user_id=current_user.id).order_by(
        VerificationRequest.created_at.desc()
    )
    return render_template("verification/become_seller.html", my_requests=my_requests)
