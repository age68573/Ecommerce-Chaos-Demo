from flask import Blueprint, render_template, request, redirect, url_for, session
from app.services import cart_service

cart_bp = Blueprint("cart", __name__, url_prefix="/cart")


@cart_bp.before_request
def require_login():
    # 只有登入（註冊會員）才可以使用購物車
    if not session.get("user_id"):
        return redirect(url_for("auth.login", next=request.path))


@cart_bp.route("/")
def cart_view():
    summary = cart_service.get_cart_summary()
    return render_template(
        "cart/cart.html",
        cart=summary,
        page_name="Cart",
    )


@cart_bp.route("/add", methods=["POST"])
def cart_add():
    product_id = int(request.form.get("product_id"))
    qty = int(request.form.get("qty", 1))
    cart_service.add_item(product_id, qty)
    return redirect(url_for("cart.cart_view"))


@cart_bp.route("/update", methods=["POST"])
def cart_update():
    """
    批次更新數量：form 裡帶 qty_<product_id>
    """
    for k, v in request.form.items():
        if not k.startswith("qty_"):
            continue
        pid = int(k.replace("qty_", ""))
        try:
            qty = int(v)
        except ValueError:
            qty = 1
        cart_service.set_qty(pid, qty)

    return redirect(url_for("cart.cart_view"))


@cart_bp.route("/remove", methods=["POST"])
def cart_remove():
    product_id = int(request.form.get("product_id"))
    cart_service.remove_item(product_id)
    return redirect(url_for("cart.cart_view"))


@cart_bp.route("/clear", methods=["POST"])
def cart_clear():
    cart_service.clear()
    return redirect(url_for("cart.cart_view"))

