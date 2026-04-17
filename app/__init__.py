import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

# Load .env file variables into environment
load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # ── Core config ───────────────────────────────────────────
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "your-secret-key-change-in-production"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///insurance.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ── OpenAI key — loaded from .env ─────────────────────────
    app.config["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")

    # ── Extensions ────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view            = "auth.login"
    login_manager.login_message         = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    # ── Blueprints ────────────────────────────────────────────
    from .routes import main
    app.register_blueprint(main)

    from .auth import auth
    app.register_blueprint(auth)

    # ── Create DB tables ──────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app


# ── ADD THESE 3 LINES to create_app() in __init__.py ──────────
# Place them AFTER db.create_all() and BEFORE return app

    # ── Initialize RAG Knowledge Base ─────────────────────────
    # Pre-loads ChromaDB with Indian insurance knowledge on startup
    with app.app_context():
        try:
            from .agents.knowledge_base import initialize_knowledge_base
            initialize_knowledge_base()
        except Exception as e:
            print(f"[Startup] RAG init skipped: {e}")