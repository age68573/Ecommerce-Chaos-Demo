from app.database import db
from app.models.base import BaseModel


class Product(BaseModel):
    __tablename__ = "products"

    name = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(1), nullable=False)    # 'M' / 'F' / 'K'
    season = db.Column(db.String(20), nullable=False)   # 'spring'/'summer'/'fall'/'winter'
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text, nullable=True)
    active = db.Column(db.Boolean, default=True)

    images = db.relationship(
        "ProductImage",
        back_populates="product",
        lazy="select"      # 之後我們可以用 N+1 測試在這裡動手腳
    )
