from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.user_model import create_user, find_user_by_email, find_user_by_id, update_user_profile
from utils.auth import current_user, login_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.context_processor
def inject_current_user():
    return {"current_user": current_user()}


@auth_bp.route("/")
def index():
    return render_template("index.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")

        if not all([name, email, phone, password]):
            flash("Please fill in all required fields.", "error")
            return render_template("register.html")
        if find_user_by_email(email):
            flash("An account with this email already exists.", "error")
            return render_template("register.html")

        user = create_user(name=name, email=email, phone=phone, password=password)
        session["user_id"] = str(user["_id"])
        flash("Welcome to CampusLoop. Your account has been created.", "success")
        return redirect(url_for("product.dashboard"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = find_user_by_email(email)
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        session["user_id"] = str(user["_id"])
        flash(f"Welcome back, {user['name']}.", "success")
        return redirect(url_for("product.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.index"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        if not all([name, phone]):
            flash("Name and phone are required.", "error")
            return render_template("profile.html", profile_user=user)

        update_user_profile(str(user["_id"]), name=name, phone=phone)
        flash("Profile updated successfully.", "success")
        return redirect(url_for("auth.profile"))

    fresh_user = find_user_by_id(str(user["_id"]))
    return render_template("profile.html", profile_user=fresh_user)
