from functools import wraps

from flask import flash, redirect, session, url_for

from models.user_model import find_user_by_id


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    try:
        return find_user_by_id(user_id)
    except Exception:
        return None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash("Please log in to continue.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def seller_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user:
            flash("Please log in to continue.", "error")
            return redirect(url_for("auth.login"))
        if not user.get("is_verified_seller"):
            flash("Only admin-approved verified sellers can list products.", "error")
            return redirect(url_for("admin.seller_verification"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user:
            flash("Please log in to continue.", "error")
            return redirect(url_for("auth.login"))
        if user.get("role") != "admin":
            flash("Admin access is required for this page.", "error")
            return redirect(url_for("product.dashboard"))
        return view(*args, **kwargs)

    return wrapped
