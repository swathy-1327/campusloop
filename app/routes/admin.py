from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Product, RentRequest, UnavailableProductRequest, User, VerificationRequest
from app.services.trust_service import apply_trust_change


admin_bp = Blueprint("admin", __name__)


def admin_required():
    if not current_user.is_authenticated or not current_user.is_admin():
        abort(403)


@admin_bp.route("/")
@login_required
def dashboard():
    admin_required()
    role_filter = (request.args.get("role", "both").strip().lower() or "both")
    user_search = request.args.get("user_q", "").strip()
    product_query = request.args.get("product_q", "").strip()
    category = request.args.get("category", "").strip()
    mode = request.args.get("mode", "").strip()

    pending_requests = VerificationRequest.query.filter_by(status="pending").all()

    users_query = User.query
    if role_filter == "seller":
        users_query = users_query.filter(User.role == "seller")
    elif role_filter == "buyer":
        users_query = users_query.filter(User.role == "buyer")
    if user_search:
        users_query = users_query.filter(
            (User.name.ilike(f"%{user_search}%"))
            | (User.email.ilike(f"%{user_search}%"))
            | (User.phone.ilike(f"%{user_search}%"))
        )
    users = users_query.order_by(User.created_at.desc()).all()

    products_query = Product.query
    if product_query:
        products_query = products_query.filter(Product.title.ilike(f"%{product_query}%"))
    if category:
        products_query = products_query.filter(Product.category == category)
    if mode:
        products_query = products_query.filter(Product.mode == mode)
    products = products_query.order_by(Product.created_at.desc()).all()

    rent_requests = RentRequest.query.order_by(RentRequest.created_at.desc()).all()
    unavailable_requests = UnavailableProductRequest.query.order_by(
        UnavailableProductRequest.created_at.desc()
    ).all()
    return render_template(
        "admin/dashboard.html",
        pending_requests=pending_requests,
        users=users,
        products=products,
        rent_requests=rent_requests,
        unavailable_requests=unavailable_requests,
        role_filter=role_filter,
        user_search=user_search,
        product_query=product_query,
        selected_category=category,
        selected_mode=mode,
    )


@admin_bp.route("/verification/<int:request_id>/<action>", methods=["POST"])
@login_required
def handle_verification(request_id, action):
    admin_required()
    verification_request = VerificationRequest.query.get_or_404(request_id)
    user = verification_request.user

    if action == "approve":
        verification_request.status = "approved"
        user.is_verified_seller = True
        user.role = "seller"
        apply_trust_change(user, 30, "Seller verification approved", "verification")
        flash("Seller approved.", "success")
    elif action == "reject":
        verification_request.status = "rejected"
        flash("Seller rejected.", "warning")
    else:
        abort(400)

    verification_request.reviewed_at = datetime.utcnow()
    verification_request.reviewed_by_admin = current_user.id
    verification_request.admin_remark = request.form.get("admin_remark", "").strip()
    db.session.commit()
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/users/<int:user_id>/toggle-status", methods=["POST"])
@login_required
def toggle_user_status(user_id):
    admin_required()
    user = User.query.get_or_404(user_id)
    user.account_status = "blocked" if user.account_status == "active" else "active"
    db.session.commit()
    flash("User status updated.", "info")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/users/<int:user_id>/set-role", methods=["POST"])
@login_required
def set_user_role(user_id):
    admin_required()
    user = User.query.get_or_404(user_id)
    new_role = request.form.get("role", "buyer").strip()
    if new_role not in {"buyer", "seller", "admin"}:
        abort(400)

    user.role = new_role
    if new_role == "seller":
        user.is_verified_seller = True
    db.session.commit()
    flash("User role updated.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/seller-verification", methods=["GET", "POST"])
@login_required
def seller_verification():
    if request.method == "POST":
        existing = VerificationRequest.query.filter_by(
            user_id=current_user.id,
            status="pending",
        ).first()
        if existing:
            flash("You already have a pending verification request.", "warning")
            return redirect(url_for("admin.seller_verification"))

        verification_request = VerificationRequest(
            user_id=current_user.id,
            id_type=request.form["id_type"].strip(),
            id_document_ref=request.form["id_document_ref"].strip(),
            status="pending",
        )
        db.session.add(verification_request)
        db.session.commit()
        flash("Verification request submitted to admin.", "success")
        return redirect(url_for("admin.seller_verification"))

    existing_requests = VerificationRequest.query.filter_by(user_id=current_user.id).order_by(
        VerificationRequest.created_at.desc()
    ).all()
    return render_template("verification/become_seller.html", my_requests=existing_requests)


@admin_bp.route("/products/<int:product_id>/remove", methods=["POST"])
@login_required
def remove_product(product_id):
    admin_required()
    product = Product.query.get_or_404(product_id)
    product.removed_by_admin = True
    product.product_status = "removed"
    product.removal_reason = request.form.get("reason", "").strip() or "Removed by admin"
    apply_trust_change(product.seller, -15, "Fake or suspicious listing", "penalty")
    db.session.commit()
    flash("Product removed.", "warning")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@login_required
def delete_product(product_id):
    admin_required()
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted permanently.", "warning")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    admin_required()
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted permanently.", "warning")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/products/<int:product_id>/restore", methods=["POST"])
@login_required
def restore_product(product_id):
    admin_required()
    product = Product.query.get_or_404(product_id)
    product.removed_by_admin = False
    product.product_status = "available"
    product.removal_reason = None
    db.session.commit()
    flash("Product restored.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/requests/rent/<int:request_id>/close", methods=["POST"])
@login_required
def close_rent_request(request_id):
    admin_required()
    rent_request = RentRequest.query.get_or_404(request_id)
    rent_request.status = "closed"
    db.session.commit()
    flash("Rent request closed.", "info")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/requests/unavailable/<int:request_id>/close", methods=["POST"])
@login_required
def close_unavailable_request(request_id):
    admin_required()
    unavailable_request = UnavailableProductRequest.query.get_or_404(request_id)
    unavailable_request.status = "closed"
    db.session.commit()
    flash("Unavailable-item request closed.", "info")
    return redirect(url_for("admin.dashboard"))
