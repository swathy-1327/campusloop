from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with that email already exists.", "danger")
            return redirect(url_for("auth.register"))

        user = User(
            name=request.form["name"].strip(),
            email=email,
            password_hash=generate_password_hash(request.form["password"]),
            phone=request.form["phone"].strip(),
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, request.form["password"]):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        if user.account_status != "active":
            flash("Your account is not active.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user)
        flash("Welcome back.", "success")
        return redirect(url_for("main.index"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing_user:
            flash("That email is already in use by another account.", "danger")
            return redirect(url_for("auth.profile"))

        current_user.name = request.form["name"].strip()
        current_user.email = email
        current_user.phone = request.form["phone"].strip()

        new_password = request.form.get("password", "").strip()
        if new_password:
            current_user.password_hash = generate_password_hash(new_password)

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("auth.profile"))

    return render_template("auth/profile.html")


@auth_bp.route("/setup-admin", methods=["GET", "POST"])
def setup_admin():
    existing_admin = User.query.filter_by(role="admin").first()
    if existing_admin:
        flash("An admin account already exists. Please log in.", "info")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("That email is already registered. Use a different email for the admin account.", "danger")
            return redirect(url_for("auth.setup_admin"))

        admin = User(
            name=request.form["name"].strip(),
            email=email,
            password_hash=generate_password_hash(request.form["password"]),
            phone=request.form["phone"].strip(),
            role="admin",
            account_status="active",
            trust_score=75,
            trust_level="Highly Trusted",
            is_verified_seller=True,
        )
        db.session.add(admin)
        db.session.commit()
        login_user(admin)
        flash("First admin account created successfully.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("auth/setup_admin.html")
