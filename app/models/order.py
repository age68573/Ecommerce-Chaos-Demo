from datetime import datetime
from app.database import db

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)

    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(32), nullable=False, default="created")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship(
        "OrderItem",
        backref="order",
        lazy="select",
        cascade="all, delete-orphan",
    )
