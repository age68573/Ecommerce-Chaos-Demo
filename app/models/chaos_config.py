from app.database import db
from app.models.base import BaseModel


class ChaosConfig(BaseModel):
    """
    簡單的 key-value 存放混沌設定
    例如：
      key="slow_product_list", value="true"
    """
    __tablename__ = "chaos_config"

    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String(200), nullable=False)

    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        cfg = ChaosConfig.query.filter_by(key=key).first()
        if not cfg:
            return default
        return cfg.value.lower() in ("1", "true", "yes", "on")

    @staticmethod
    def set_bool(key: str, flag: bool):
        cfg = ChaosConfig.query.filter_by(key=key).first()
        if not cfg:
            cfg = ChaosConfig(key=key, value="true" if flag else "false")
            db.session.add(cfg)
        else:
            cfg.value = "true" if flag else "false"
        db.session.commit()
