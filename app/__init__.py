import os
import instana  # 啟用 Instana 自動追蹤

from flask import Flask, g, session
from app.config import Config
from app.database import db
from app.models.user import User


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)
    app.config.setdefault("SECRET_KEY", "change-this-in-production")
    # 初始化 DB
    db.init_app(app)

    # 註冊藍圖
    from app.controllers.home_controller import home_bp
    from app.controllers.product_controller import product_bp
    from app.controllers.chaos_controller import chaos_bp
    from app.controllers.admin_product_controller import admin_product_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.admin_user_controller import admin_user_bp
    from app.controllers.cart_controller import cart_bp
    from app.controllers.order_controller import order_bp
    from app.controllers.admin_order_controller import admin_order_bp


    app.register_blueprint(home_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(chaos_bp)
    app.register_blueprint(admin_product_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_user_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(admin_order_bp)


    # 健康檢查
    @app.route("/health")
    def health():
        return {"status": "ok"}

    # 建立資料表（開發階段方便用）
    with app.app_context():
        db.create_all() 


    # ---- 每次 request 前載入 current_user ----
    @app.before_request
    def load_current_user():
        user_id = session.get("user_id")
        if user_id is None:
            g.current_user = None
        else:
            g.current_user = User.query.get(user_id)

    # ---- 注入到 template（current_user / page_name） ----
    @app.context_processor
    def inject_common():
        return {
            "current_user": getattr(g, "current_user", None),
            # 預設 page_name 讓 base.html 可以用，個別頁面也可以 override
            "page_name": None,
        }
    return app
