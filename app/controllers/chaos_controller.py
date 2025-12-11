from flask import Blueprint, render_template, request, redirect, url_for
from app.services import chaos_service

chaos_bp = Blueprint("chaos", __name__, url_prefix="/admin/chaos")


@chaos_bp.route("/", methods=["GET", "POST"])
def chaos_panel():
    """
    混沌控制台：
    頁面上是一些 checkbox，POST 後寫入 chaos_config
    """
    keys = [
        chaos_service.SLOW_PRODUCT_LIST,
        chaos_service.NPLUS1_IMAGES,
        chaos_service.SLOW_IMAGES,
        chaos_service.BROKEN_IMAGES,
        chaos_service.IMAGE_PERMISSION,
    ]

    if request.method == "POST":
        for key in keys:
            flag = bool(request.form.get(key))
            chaos_service.set_flag(key, flag)
        return redirect(url_for("chaos.chaos_panel"))

    # GET：把目前的設定帶回頁面
    flags = {key: chaos_service.is_enabled(key) for key in keys}
    return render_template("admin/chaos.html", flags=flags)
