from flask import Blueprint, render_template, redirect, url_for, session, abort
from app.models.order import Order
from app.services.order_service import create_order_from_cart

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

    return render_template("orders/order_detail.html", order=order)
