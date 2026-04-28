from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, abort
from flask_login import login_required, current_user
from .models import Policy
from . import db
import os

main = Blueprint("main", __name__)

# ── Allowed IRDAI PDFs ─────────────────────────────────────────
ALLOWED_PDFS = {
    "irdai-regulatory-outlook": "2026-insurance-regulatory-outlook.pdf",
    "irdai-ind-as-circular":    "IRDAI Ind AS Circular 01.04.2026.pdf",
}


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
        except Exception:
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
        except Exception:
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


# ── DOWNLOAD IRDAI PDF ────────────────────────────────────────
@main.route("/download-pdf/<key>")
@login_required
def download_pdf(key):
    filename = ALLOWED_PDFS.get(key)
    if not filename:
        abort(404)
    # PDF lives in the project root (one level up from the app package)
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
    filepath = os.path.join(project_root, filename)
    if not os.path.isfile(filepath):
        abort(404)
    return send_file(filepath, as_attachment=True, download_name=filename)


# ── API: POLICY DISTRIBUTION (Pie Chart) ─────────────────────
@main.route("/api/policy-distribution")
@login_required
def policy_distribution():
    """
    Returns policy-type counts for the current user.
    Used by the home-page pie chart section.
    Response: { labels: [...], counts: [...] }
    """
    from sqlalchemy import func
    rows = (
        db.session.query(
            Policy.policy_type,
            func.count(Policy.id).label("cnt")
        )
        .filter(Policy.user_id == current_user.id)
        .group_by(Policy.policy_type)
        .all()
    )
    labels = [r.policy_type for r in rows]
    counts = [r.cnt        for r in rows]
    return jsonify({"labels": labels, "counts": counts})


# ── AI STUDIO PAGE ────────────────────────────────────────────
@main.route("/ai-studio", methods=["GET", "POST"])
@login_required
def ai_studio():
    return render_template("ai_studio.html")


# ── AGENT UI PAGE ─────────────────────────────────────────────
# Separate page for the multi-agent RAG pipeline
@main.route("/agent-ui")
@login_required
def agent_ui():
    return render_template("agent_ui.html")


# ═══════════════════════════════════════════════════════════════
# JSON API ENDPOINTS
# ═══════════════════════════════════════════════════════════════

# ── API: ASYNC TEXT EXPLANATION (single LLM) ──────────────────
@main.route("/api/explain", methods=["POST"])
@login_required
def explain_api():
    """
    Single-LLM endpoint — fast, used by AI Studio Policy Explainer tab.
    Returns: { success, explanation }
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


# ── API: ASYNC IMAGE GENERATION ───────────────────────────────
@main.route("/api/generate-image", methods=["POST"])
@login_required
def generate_image_api():
    """
    Image generation endpoint — used by AI Studio Infographic tab.
    Returns: { success, image_url (base64 data URL) }
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


# ── API: MULTI-AGENT RAG PIPELINE ────────────────────────────
@main.route("/api/agent-explain", methods=["POST"])
@login_required
def agent_explain_api():
    """
    Multi-Agent endpoint: ResearcherAgent → WriterAgent pipeline.

    Flow:
      1. ResearcherAgent queries ChromaDB RAG (India knowledge base)
      2. ResearcherAgent runs supplementary LLM research
      3. Handoff Gate validates ResearchPacket
      4. WriterAgent synthesizes into structured Indian-market response
      5. Returns content + full pipeline metadata

    Returns: {
        success, explanation, policy_type, confidence,
        sources_used, agents_involved, total_time_s,
        pipeline_logs, mode
    }
    """
    try:
        data        = request.get_json()
        user_prompt = data.get("prompt", "").strip()
        policy_type = data.get("policy_type", None)

        if not user_prompt:
            return jsonify({"success": False, "error": "Prompt is empty."})

        # Import orchestrator — singleton, initialised once
        from .agents.orchestrator import get_orchestrator
        orchestrator = get_orchestrator()
        result       = orchestrator.run(user_prompt, policy_type)

        return jsonify({
            "success"         : True,
            "explanation"     : result["content"],
            "policy_type"     : result["policy_type"],
            "confidence"      : result["confidence"],
            "sources_used"    : result["sources_used"],
            "agents_involved" : result["agents_involved"],
            "total_time_s"    : result["total_time_s"],
            "pipeline_logs"   : result["pipeline_logs"],
            "mode"            : "multi_agent_rag"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})