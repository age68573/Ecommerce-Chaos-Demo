from typing import Dict
from app.database import db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.services.cart_service import get_cart_summary, clear as clear_cart


def create_order_from_cart(user_id: int) -> Order:
    """
    將目前購物車轉成一筆訂單（同步）
    """
    cart = get_cart_summary()
    if not cart["items"]:
        raise ValueError("Cart is empty")

    order = Order(
        user_id=user_id,
        total_amount=cart["subtotal"],
        status="created",
    )
    db.session.add(order)
    db.session.flush()  # 取得 order.id（不 commit）

    for item in cart["items"]:
        p = item["product"]
        oi = OrderItem(
            order_id=order.id,
            product_id=p.id,
            product_name=p.name,
            unit_price=p.price,
            quantity=item["qty"],
        )
        db.session.add(oi)

    db.session.commit()

    # 清空購物車
    clear_cart()

    return order
