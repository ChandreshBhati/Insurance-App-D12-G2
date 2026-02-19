from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Policy
from . import db

main = Blueprint('main', __name__)


# ==============================
# HOME
# ==============================
@main.route("/")
def home():
    policies = Policy.query.order_by(Policy.id.desc()).all()
    return render_template("index.html", policies=policies)


# ==============================
# POLICY SECTIONS
# ==============================
@main.route("/health-policy")
def health():
    return render_template("health.html")


@main.route("/term-policy")
def term():
    return render_template("term.html")


@main.route("/vehicle-policy")
def vehicle():
    return render_template("vehicle.html")


# ==============================
# CREATE POLICY
# ==============================
@main.route("/add-policy", methods=["GET", "POST"])
def add_policy():
    if request.method == "POST":
        try:
            new_policy = Policy(
                policy_type=request.form.get("policy_type"),
                customer_name=request.form.get("customer_name"),
                email=request.form.get("email"),
                premium_amount=float(request.form.get("premium_amount"))
            )

            db.session.add(new_policy)
            db.session.commit()

            flash("Policy added successfully!", "success")
            return redirect(url_for("main.home"))

        except Exception as e:
            db.session.rollback()
            flash("Error adding policy. Please try again.", "danger")

    return render_template("add_policy.html")


# ==============================
# EDIT POLICY
# ==============================
@main.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_policy(id):
    policy = Policy.query.get_or_404(id)

    if request.method == "POST":
        try:
            policy.policy_type = request.form.get("policy_type")
            policy.customer_name = request.form.get("customer_name")
            policy.email = request.form.get("email")
            policy.premium_amount = float(request.form.get("premium_amount"))

            db.session.commit()

            flash("Policy updated successfully!", "success")
            return redirect(url_for("main.home"))

        except Exception as e:
            db.session.rollback()
            flash("Error updating policy.", "danger")

    return render_template("edit_policy.html", policy=policy)


# ==============================
# DELETE POLICY (POST SAFE)
# ==============================
@main.route("/delete/<int:id>", methods=["POST"])
def delete_policy(id):
    policy = Policy.query.get_or_404(id)

    try:
        db.session.delete(policy)
        db.session.commit()
        flash("Policy deleted successfully!", "success")

    except Exception:
        db.session.rollback()
        flash("Error deleting policy.", "danger")

    return redirect(url_for("main.home"))
