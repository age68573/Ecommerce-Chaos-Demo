from flask import Blueprint, render_template, redirect, url_for, session, abort
from app.models.order import Order
from app.services.order_service import create_order_from_cart
from app.services.payment_service import start_payment, finalize_payment_if_pending



order_bp = Blueprint("order", __name__, url_prefix="/orders")


@order_bp.before_request
def require_login():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))


@order_bp.route("/checkout", methods=["POST"])
def checkout():
    user_id = session["user_id"]
    try:
        order = create_order_from_cart(user_id)
    except ValueError:
        return redirect(url_for("cart.cart_view"))

    return redirect(url_for("order.order_detail", order_id=order.id))


@order_bp.route("/")
def my_orders():
    user_id = session["user_id"]
    orders = (
        Order.query
        .filter_by(user_id=user_id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return render_template("orders/order_list.html", orders=orders)


@order_bp.route("/<int:order_id>")
def order_detail(order_id: int):
    order = Order.query.get(order_id)
    if not order:
        abort(404)

    if order.user_id != session["user_id"]:
        abort(403)

    # ⭐ 關鍵：這是一個「新的 HTTP request」
    if order.status == "pending":
        finalize_payment_if_pending(order.id)
        order = Order.query.get(order_id)

    return render_template(
        "orders/order_detail.html",
        order=order,
        page_name=f"Order {order.id}"
    )



@order_bp.route("/<int:order_id>/pay", methods=["POST"])
def pay_order(order_id: int):
    order = Order.query.get(order_id)
    if not order:
        abort(404)

    if order.user_id != session["user_id"]:
        abort(403)

    if order.status not in ("created", "failed"):
        return redirect(url_for("order.order_detail", order_id=order.id))

    # ✅ 只做 pending
    start_payment(order.id)

    # ✅ 立刻 redirect（這一步非常重要）
    return redirect(url_for("order.order_detail", order_id=order.id))
