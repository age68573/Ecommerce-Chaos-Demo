from datetime import datetime
from app.database import db


class BaseModel(db.Model):
    """
    給其他 model 繼承的 base：
    - id 主鍵
    - created_at
    """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
