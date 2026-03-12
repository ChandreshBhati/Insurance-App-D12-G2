from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Policy
from . import db

main = Blueprint("main", __name__)


# ── HOME ──────────────────────────────────────────────────────
@main.route("/")
@login_required
def home():
    policies = Policy.query.filter_by(user_id=current_user.id)\
                           .order_by(Policy.id.desc()).all()
    return render_template("index.html", policies=policies)


# ── POLICY INFO SECTIONS ──────────────────────────────────────
@main.route("/health-policy")
@login_required
def health():
    return render_template("health.html")


@main.route("/term-policy")
@login_required
def term():
    return render_template("term.html")


@main.route("/vehicle-policy")
@login_required
def vehicle():
    return render_template("vehicle.html")


# ── CREATE POLICY ─────────────────────────────────────────────
@main.route("/add-policy", methods=["GET", "POST"])
@login_required
def add_policy():
    if request.method == "POST":
        try:
            new_policy = Policy(
                policy_type    = request.form.get("policy_type"),
                customer_name  = request.form.get("customer_name"),
                email          = request.form.get("email"),
                premium_amount = float(request.form.get("premium_amount")),
                user_id        = current_user.id
            )
            db.session.add(new_policy)
            db.session.commit()
            flash("Policy added successfully!", "success")
            return redirect(url_for("main.home"))

        except Exception as e:
            db.session.rollback()
            flash("Error adding policy. Please try again.", "danger")

    return render_template("add_policy.html")


# ── EDIT POLICY ───────────────────────────────────────────────
@main.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_policy(id):
    policy = Policy.query.get_or_404(id)

    if policy.user_id != current_user.id:
        flash("You are not authorised to edit this policy.", "danger")
        return redirect(url_for("main.home"))

    if request.method == "POST":
        try:
            policy.policy_type    = request.form.get("policy_type")
            policy.customer_name  = request.form.get("customer_name")
            policy.email          = request.form.get("email")
            policy.premium_amount = float(request.form.get("premium_amount"))
            db.session.commit()
            flash("Policy updated successfully!", "success")
            return redirect(url_for("main.home"))

        except Exception as e:
            db.session.rollback()
            flash("Error updating policy.", "danger")

    return render_template("edit_policy.html", policy=policy)


# ── DELETE POLICY ─────────────────────────────────────────────
@main.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_policy(id):
    policy = Policy.query.get_or_404(id)

    if policy.user_id != current_user.id:
        flash("You are not authorised to delete this policy.", "danger")
        return redirect(url_for("main.home"))

    try:
        db.session.delete(policy)
        db.session.commit()
        flash("Policy deleted successfully!", "success")

    except Exception:
        db.session.rollback()
        flash("Error deleting policy.", "danger")

    return redirect(url_for("main.home"))


# ── AI STUDIO ─────────────────────────────────────────────────
@main.route("/ai-studio", methods=["GET", "POST"])
@login_required
def ai_studio():
    explanation = None
    image_url   = None
    error       = None
    active_tab  = "explain"   # which tab to show after POST

    if request.method == "POST":
        action      = request.form.get("action")
        policy_type = request.form.get("policy_type", "Health Insurance")
        user_prompt = request.form.get("prompt", "").strip()
        active_tab  = action  # keep the right tab open after submit

        if not user_prompt:
            error = "Please enter a prompt before submitting."
        else:
            try:
                # Import here to avoid circular imports
                from .ai import generate_policy_explanation, generate_risk_infographic

                if action == "explain":
                    explanation = generate_policy_explanation(
                        user_prompt, policy_type
                    )

                elif action == "visualize":
                    image_url = generate_risk_infographic(
                        policy_type, user_prompt
                    )

            except Exception as e:
                # Catch API errors gracefully
                err_str = str(e)
                if "api_key" in err_str.lower() or "authentication" in err_str.lower():
                    error = "Invalid or missing OpenAI API key. Please check your .env file."
                elif "quota" in err_str.lower() or "billing" in err_str.lower():
                    error = "OpenAI quota exceeded. Please check your billing at platform.openai.com."
                elif "rate" in err_str.lower():
                    error = "Too many requests. Please wait a moment and try again."
                else:
                    error = f"AI service error: {err_str}"

    return render_template("ai_studio.html",
                           explanation=explanation,
                           image_url=image_url,
                           error=error,
                           active_tab=active_tab)