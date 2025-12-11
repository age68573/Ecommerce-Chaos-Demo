import os
import instana  # 啟用 Instana 自動追蹤

from flask import Flask
from app.config import Config
from app.database import db


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)

    # 初始化 DB
    db.init_app(app)

    # 註冊藍圖
    from app.controllers.home_controller import home_bp
    from app.controllers.product_controller import product_bp
    from app.controllers.chaos_controller import chaos_bp
    from app.controllers.admin_product_controller import admin_product_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(chaos_bp)
    app.register_blueprint(admin_product_bp)


    # 健康檢查
    @app.route("/health")
    def health():
        return {"status": "ok"}

    # 建立資料表（開發階段方便用）
    with app.app_context():
        db.create_all()

    return app
