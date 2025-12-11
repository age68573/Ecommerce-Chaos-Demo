from flask import Blueprint, render_template

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def home():
    # 簡單首頁，之後可做推薦 / 熱門商品
    return render_template("home.html")
