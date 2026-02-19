from . import db

class Policy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    policy_type = db.Column(db.String(100), nullable=False)
    customer_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    premium_amount = db.Column(db.Float, nullable=False)



