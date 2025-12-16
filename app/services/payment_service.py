import random
import time
from app.database import db
from app.models.order import Order


def start_payment(order_id: int) -> Order:
    """
    第一步：把訂單狀態設成 pending，立刻回應（讓 UI 顯示 loading）
    """
    order = Order.query.get(order_id)
    if not order:
        raise ValueError("Order not found")

    if order.status not in ("created", "failed"):
        return order

    order.status = "pending"
    db.session.commit()
    return order


def finalize_payment_if_pending(order_id: int) -> Order:
    """
    第二步：只要還在 pending，就執行「真正的假金流處理」並回寫 paid/failed
    這段會被 pending 頁面自動刷新觸發
    """
    order = Order.query.get(order_id)
    if not order:
        raise ValueError("Order not found")

    if order.status != "pending":
        return order

    # 模擬金流延遲（你可以調大一點更容易看見 spinner）
    time.sleep(random.uniform(1.0, 3.0))

    success = random.random() < 0.7
    order.status = "paid" if success else "failed"
    db.session.commit()
    return order
