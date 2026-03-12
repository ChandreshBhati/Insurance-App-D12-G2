from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from . import db

auth = Blueprint("auth", __name__)


# ── REGISTER ─────────────────────────────────────────────────
@auth.route("/register", methods=["GET", "POST"])
def register():
    # Already logged in? Send home
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        # ── Basic validations ──────────────────────────────
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "danger")
            return render_template("register.html")

        if User.query.filter_by(username=username).first():
            flash("That username is already taken.", "danger")
            return render_template("register.html")

        # ── Create user ────────────────────────────────────
        try:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            # Log them in immediately after registration
            login_user(new_user)
            flash(f"Welcome, {new_user.username}! Your account has been created.", "success")
            return redirect(url_for("main.home"))

        except Exception as e:
            db.session.rollback()
            flash("Something went wrong. Please try again.", "danger")

    return render_template("register.html")


# ── LOGIN ─────────────────────────────────────────────────────
@auth.route("/login", methods=["GET", "POST"])
def login():
    # Already logged in? Send home
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = True if request.form.get("remember") else False

        if not email or not password:
            flash("Please enter your email and password.", "danger")
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()

        # Check user exists AND password is correct
        if not user or not user.check_password(password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template("login.html")

        login_user(user, remember=remember)
        flash(f"Welcome back, {user.username}!", "success")

        # Redirect to the page they were trying to visit, or home
        next_page = request.args.get("next")
        return redirect(next_page or url_for("main.home"))

    return render_template("login.html")


# ── LOGOUT ───────────────────────────────────────────────────
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("auth.login"))