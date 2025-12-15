from typing import Dict, Any, List, Tuple
from flask import session
from app.models.product import Product


CART_SESSION_KEY = "cart_items"  # { "<product_id>": quantity }


def _get_cart_dict() -> Dict[str, int]:
    cart = session.get(CART_SESSION_KEY)
    if not isinstance(cart, dict):
        cart = {}
        session[CART_SESSION_KEY] = cart
    return cart


def add_item(product_id: int, qty: int = 1) -> None:
    cart = _get_cart_dict()
    key = str(product_id)
    cart[key] = int(cart.get(key, 0)) + int(qty)
    if cart[key] <= 0:
        cart.pop(key, None)
    session.modified = True


def set_qty(product_id: int, qty: int) -> None:
    cart = _get_cart_dict()
    key = str(product_id)
    qty = int(qty)
    if qty <= 0:
        cart.pop(key, None)
    else:
        cart[key] = qty
    session.modified = True


def remove_item(product_id: int) -> None:
    cart = _get_cart_dict()
    cart.pop(str(product_id), None)
    session.modified = True


def clear() -> None:
    session.pop(CART_SESSION_KEY, None)
    session.modified = True


def get_cart_summary() -> Dict[str, Any]:
    """
    回傳：
    - items: [{product, qty, line_total}]
    - subtotal
    - total_qty
    """
    cart = _get_cart_dict()
    ids = [int(pid) for pid in cart.keys()] if cart else []
    products = Product.query.filter(Product.id.in_(ids)).all() if ids else []

    # 用 dict 快速對應
    product_map = {p.id: p for p in products}

    items: List[Dict[str, Any]] = []
    subtotal = 0.0
    total_qty = 0

    for pid_str, qty in cart.items():
        pid = int(pid_str)
        p = product_map.get(pid)
        if not p:
            # 商品已被刪掉，但購物車還有 -> 直接忽略/清掉
            continue
        qty = int(qty)
        line_total = float(p.price) * qty
        items.append({"product": p, "qty": qty, "line_total": line_total})
        subtotal += line_total
        total_qty += qty

    return {"items": items, "subtotal": subtotal, "total_qty": total_qty}
