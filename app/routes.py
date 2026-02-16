from flask import Blueprint, render_template, request, redirect

main_routes = Blueprint("main", __name__, template_folder="templates")

policies = []

@main_routes.route("/")
def home():
    return render_template("index.html", policies=policies)

@main_routes.route("/add", methods=["POST"])
def add_policy():
    name = request.form.get("name")
    policy_type = request.form.get("type")
    amount = request.form.get("amount")

    policies.append({
        "name": name,
        "type": policy_type,
        "amount": amount
    })

    return redirect("/")
    
@main_routes.route("/health")
def health():
    return {"status": "UP"}, 200
