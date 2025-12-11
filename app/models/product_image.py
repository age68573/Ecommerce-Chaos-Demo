from app.database import db
from app.models.base import BaseModel


class ProductImage(BaseModel):
    __tablename__ = "product_images"

    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    is_main = db.Column(db.Boolean, default=False)

    product = db.relationship("Product", back_populates="images")
