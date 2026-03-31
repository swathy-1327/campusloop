from flask import Blueprint, flash, redirect, render_template, request, url_for

from models.product_model import (
    admin_delete_product,
    admin_edit_product,
    admin_update_product_status,
    find_product_by_id,
    list_marketplace_products,
)
from models.user_model import (
    admin_delete_user,
    admin_update_user_status,
    find_user_by_id,
    list_users_filtered,
)
from models.verification_model import create_verification_request, get_pending_requests, list_requests_for_user, review_verification_request
from services.trust_service import apply_trust_event
from utils.auth import admin_required, current_user, login_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/seller-verification", methods=["GET", "POST"])
@login_required
def seller_verification():
    user = current_user()
    existing_requests = list_requests_for_user(str(user["_id"]))
    if request.method == "POST":
        id_type = request.form.get("id_type", "").strip()
        id_document_url = request.form.get("id_document_url", "").strip()
        if not all([id_type, id_document_url]):
            flash("ID type and proof reference are required.", "error")
            return render_template("seller_verification.html", existing_requests=existing_requests)

        create_verification_request(str(user["_id"]), id_type, id_document_url)
        flash("Verification request submitted to admin.", "success")
        return redirect(url_for("admin.seller_verification"))

    return render_template("seller_verification.html", existing_requests=existing_requests)


@admin_bp.route("/dashboard")
@admin_required
def admin_dashboard():
    role_filter = request.args.get("role", "both").strip().lower() or "both"
    user_search = request.args.get("user_q", "").strip()
    product_query = request.args.get("product_q", "").strip()
    category = request.args.get("category", "").strip()
    mode = request.args.get("mode", "").strip()
    return render_template(
        "admin_dashboard.html",
        pending_requests=get_pending_requests(),
        users=list_users_filtered(role_filter=role_filter, search=user_search),
        products=list_marketplace_products(
            query=product_query,
            category=category,
            mode=mode,
            include_inactive=True,
        ),
        role_filter=role_filter,
        user_search=user_search,
        product_query=product_query,
        selected_category=category,
        selected_mode=mode,
    )


@admin_bp.route("/verification/<request_id>/review", methods=["POST"])
@admin_required
def review_request(request_id):
    admin = current_user()
    decision = request.form.get("decision", "").strip()
    remark = request.form.get("remark", "").strip()
    verification_request = review_verification_request(request_id, decision, remark, str(admin["_id"]))
    if not verification_request:
        flash("Verification request not found.", "error")
        return redirect(url_for("admin.admin_dashboard"))

    if decision == "approved":
        user = find_user_by_id(verification_request["user_id"])
        if user:
            admin_update_user_status(verification_request["user_id"], is_verified_seller=True)
            apply_trust_event(verification_request["user_id"], "seller_verification_approved")

    flash(f"Verification request {decision}.", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/users/<user_id>/status", methods=["POST"])
@admin_required
def update_user_status(user_id):
    admin_update_user_status(user_id, account_status=request.form.get("account_status", "active"))
    flash("User status updated.", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/users/<user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    admin_delete_user(user_id)
    flash("User removed from the platform.", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/products/<product_id>/status", methods=["POST"])
@admin_required
def update_product_status(product_id):
    admin_update_product_status(
        product_id,
        request.form.get("product_status", "active"),
        request.form.get("removal_reason", "").strip(),
    )
    flash("Product moderation updated.", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/products/<product_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_product(product_id):
    product = find_product_by_id(product_id)
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("admin.admin_dashboard"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        use_type = request.form.get("use_type", "").strip()
        price = request.form.get("price", "").strip()
        condition = request.form.get("condition", "").strip()
        mode = request.form.get("mode", "").strip()
        description = request.form.get("description", "").strip()

        if not all([title, category, use_type, price, condition, mode, description]):
            flash("All product fields are required for admin editing.", "error")
            return render_template("admin_product_edit.html", product=product)

        admin_edit_product(
            product_id,
            title=title,
            category=category,
            use_type=use_type,
            price=float(price),
            condition=condition,
            mode=mode,
            description=description,
        )
        flash("Product details updated.", "success")
        return redirect(url_for("admin.admin_dashboard"))

    return render_template("admin_product_edit.html", product=product)


@admin_bp.route("/products/<product_id>/delete", methods=["POST"])
@admin_required
def delete_product(product_id):
    admin_delete_product(product_id)
    flash("Product removed from the platform.", "success")
    return redirect(url_for("admin.admin_dashboard"))
