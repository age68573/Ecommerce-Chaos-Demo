from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, abort
from app.database import db
from app.models.order import Order

admin_order_bp = Blueprint("admin_order", __name__, url_prefix="/admin/orders")

# 允許刪除的狀態（你之後接 queue 也安全）
DELETABLE_STATUSES = {"created", "failed", "cancelled"}

# 不允許刪除（保護 queue/金流一致性）
BLOCKED_DELETE_STATUSES = {"pending", "processing", "paid"}


@admin_order_bp.before_request
def require_admin():
    if not session.get("user_id") or not session.get("is_admin"):
        return redirect(url_for("auth.login", next=request.path))


@admin_order_bp.route("/")
def order_list_all():
    """
    Admin：查看所有使用者訂單
    - q：搜尋 order_id / user_id / status（簡易）
    - date_from / date_to：日期範圍（以 created_at）
    - page / per_page：分頁
    """
    q = (request.args.get("q") or "").strip()
    date_from = (request.args.get("date_from") or "").strip()  # YYYY-MM-DD
    date_to = (request.args.get("date_to") or "").strip()      # YYYY-MM-DD
    status = (request.args.get("status") or "").strip()

    # 分頁
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    if per_page not in (10, 20, 50, 100):
        per_page = 10
    if page < 1:
        page = 1

    query = Order.query

    # q 搜尋：若是數字 -> order_id 或 user_id；否則 -> status like
    if q:
        if q.isdigit():
            n = int(q)
            query = query.filter((Order.id == n) | (Order.user_id == n))
        else:
            query = query.filter(Order.status.ilike(f"%{q}%"))

    # status 篩選（精準等於）
    if status:
        query = query.filter(Order.status == status)

    # 日期範圍：date_from <= created_at < (date_to + 1 day)
    def _parse_date(s: str):
        return datetime.strptime(s, "%Y-%m-%d")

    if date_from:
        try:
            dt_from = _parse_date(date_from)
            query = query.filter(Order.created_at >= dt_from)
        except ValueError:
            date_from = ""  # 讓 UI 回填為空，避免壞格式卡住

    if date_to:
        try:
            dt_to = _parse_date(date_to) + timedelta(days=1)  # inclusive end day
            query = query.filter(Order.created_at < dt_to)
        except ValueError:
            date_to = ""

    query = query.order_by(Order.created_at.desc())

    # Flask-SQLAlchemy 通常有 paginate；若沒有就用 offset/limit fallback
    paginate_fn = getattr(query, "paginate", None)
    if callable(paginate_fn):
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        orders = pagination.items
        total = pagination.total
        pages = pagination.pages
    else:
        total = query.count()
        orders = query.offset((page - 1) * per_page).limit(per_page).all()
        pages = (total + per_page - 1) // per_page

        class _Pagination:
            def __init__(self, page, per_page, total, pages):
                self.page = page
                self.per_page = per_page
                self.total = total
                self.pages = pages
                self.has_prev = page > 1
                self.has_next = page < pages
                self.prev_num = page - 1
                self.next_num = page + 1

        pagination = _Pagination(page, per_page, total, pages)

    # 讓 UI 的 status 下拉有選項（之後你狀態變多再加就好）
    status_options = ["created", "pending", "processing", "paid", "failed", "cancelled"]

    return render_template(
        "admin/order_list.html",
        orders=orders,
        q=q,
        date_from=date_from,
        date_to=date_to,
        status=status,
        status_options=status_options,
        pagination=pagination,
        per_page=per_page,
        total=total,
        page_name="Admin Orders",
    )


@admin_order_bp.route("/<int:order_id>")
def order_detail_admin(order_id: int):
    order = Order.query.get(order_id)
    if not order:
        abort(404)

    return render_template("admin/order_detail.html", order=order, page_name=f"Admin Order {order.id}")


@admin_order_bp.route("/<int:order_id>/delete", methods=["POST"])
def order_delete_admin(order_id: int):
    order = Order.query.get(order_id)
    if not order:
        return redirect(url_for("admin_order.order_list_all"))

    # 保護：避免刪到已付款或處理中（未來接 queue/金流更重要）
    status = (order.status or "").lower()

    if status in BLOCKED_DELETE_STATUSES:
        # 直接拒絕（也可改成顯示錯誤訊息頁）
        return redirect(url_for("admin_order.order_detail_admin", order_id=order.id))

    # 若你想更嚴格，只允許 DELETABLE_STATUSES：
    if status not in DELETABLE_STATUSES:
        return redirect(url_for("admin_order.order_detail_admin", order_id=order.id))

    db.session.delete(order)  # Order model 已設 cascade delete-orphan → items 會一起刪
    db.session.commit()
    return redirect(url_for("admin_order.order_list_all"))
