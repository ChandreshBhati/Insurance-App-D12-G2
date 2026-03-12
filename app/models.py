from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


# ── Flask-Login user loader ──────────────────────────────────
# Flask-Login calls this to reload the user from the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ── User Model ───────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = "user"

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(100), unique=True, nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # One user → many policies
    policies = db.relationship("Policy", backref="owner", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


# ── Policy Model ─────────────────────────────────────────────
class Policy(db.Model):
    __tablename__ = "policy"

    id             = db.Column(db.Integer, primary_key=True)
    policy_type    = db.Column(db.String(100), nullable=False)
    customer_name  = db.Column(db.String(150), nullable=False)
    email          = db.Column(db.String(150), nullable=False)
    premium_amount = db.Column(db.Float, nullable=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key — which user owns this policy
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"<Policy {self.policy_type} - {self.customer_name}>"