from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
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


# ── AI STUDIO PAGE ────────────────────────────────────────────
@main.route("/ai-studio", methods=["GET", "POST"])
@login_required
def ai_studio():
    explanation = None
    error       = None
    active_tab  = "explain"

    if request.method == "POST":
        action      = request.form.get("action")
        policy_type = request.form.get("policy_type", "Health Insurance")
        user_prompt = request.form.get("prompt", "").strip()
        active_tab  = action

        if not user_prompt:
            error = "Please enter a prompt before submitting."
        elif action == "explain":
            try:
                from .ai import generate_policy_explanation
                explanation = generate_policy_explanation(
                    user_prompt, policy_type
                )
            except Exception as e:
                err_str = str(e)
                if "authentication" in err_str.lower():
                    error = "Invalid GROQ_API_KEY. Please check your .env file."
                elif "rate" in err_str.lower():
                    error = "Too many requests. Please wait a moment and try again."
                else:
                    error = f"AI error: {err_str}"

    return render_template("ai_studio.html",
                           explanation=explanation,
                           error=error,
                           active_tab=active_tab)


# ── API: ASYNC IMAGE GENERATION ───────────────────────────────
# Called by JavaScript fetch() — returns JSON, no page reload
@main.route("/api/generate-image", methods=["POST"])
@login_required
def generate_image_api():
    """
    Async endpoint for image generation.
    JS calls this in background → page never freezes.
    Returns: { success: true, image_url: "data:image/jpeg;base64,..." }
         or: { success: false, error: "..." }
    """
    try:
        data        = request.get_json()
        policy_type = data.get("policy_type", "Health Insurance")
        concept     = data.get("prompt", "").strip()

        if not concept:
            return jsonify({"success": False, "error": "Prompt is empty."})

        from .ai import generate_risk_infographic
        image_url = generate_risk_infographic(policy_type, concept)

        return jsonify({"success": True, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# ── API: ASYNC TEXT EXPLANATION ───────────────────────────────
# Called by JS fetch() from new chat UI — returns JSON
@main.route("/api/explain", methods=["POST"])
@login_required
def explain_api():
    """
    Async endpoint for policy explanation.
    JS calls this → returns JSON → no page reload.
    Returns: { success: true, explanation: "..." }
         or: { success: false, error: "..." }
    """
    try:
        data        = request.get_json()
        user_prompt = data.get("prompt", "").strip()
        policy_type = data.get("policy_type", "General Insurance")

        if not user_prompt:
            return jsonify({"success": False, "error": "Prompt is empty."})

        from .ai import generate_policy_explanation
        explanation = generate_policy_explanation(user_prompt, policy_type)

        return jsonify({"success": True, "explanation": explanation})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    