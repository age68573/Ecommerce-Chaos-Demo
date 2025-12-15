from flask import Blueprint, render_template, request, redirect, url_for, session
from app.database import db
from app.models.user import User

admin_user_bp = Blueprint("admin_user", __name__, url_prefix="/admin/users")


@admin_user_bp.before_request
def require_admin():
    user_id = session.get("user_id")
    is_admin = session.get("is_admin")
    if not user_id or not is_admin:
        return redirect(url_for("auth.login", next=request.path))


@admin_user_bp.route("/")
def user_list():
    """
    會員列表（可用 q 搜尋 username/email）
    """
    q = (request.args.get("q") or "").strip()
    query = User.query

    if q:
        like = f"%{q}%"
        query = query.filter((User.username.ilike(like)) | (User.email.ilike(like)))

    users = query.order_by(User.created_at.desc()).all()
    return render_template("admin/user_list.html", users=users, q=q, page_name="Admin Users")


@admin_user_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
def user_edit(user_id: int):
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for("admin_user.user_list"))

    if request.method == "GET":
        form_data = {
            "username": user.username,
            "email": user.email,
            "is_admin": bool(user.is_admin),
        }
        return render_template(
            "admin/user_edit.html",
            user=user,
            form_data=form_data,
            errors=None,
            page_name=f"Edit User {user.id}",
        )

    # POST
    username = (request.form.get("username") or "").strip()
    email = (request.form.get("email") or "").strip()
    is_admin = True if request.form.get("is_admin") == "on" else False

    errors = []
    if not username:
        errors.append("使用者名稱必填。")
    if not email:
        errors.append("Email 必填。")

    # username/email 唯一性（排除自己）
    if User.query.filter(User.username == username, User.id != user.id).first():
        errors.append("此使用者名稱已被使用。")
    if User.query.filter(User.email == email, User.id != user.id).first():
        errors.append("此 Email 已被使用。")

    # 不能把「最後一個 admin」取消 admin
    if user.is_admin and (not is_admin):
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            errors.append("不能取消最後一個 Admin 的權限。")

    if errors:
        form_data = {"username": username, "email": email, "is_admin": is_admin}
        return render_template("admin/user_edit.html", user=user, form_data=form_data, errors=errors)

    user.username = username
    user.email = email
    user.is_admin = is_admin
    db.session.commit()

    return redirect(url_for("admin_user.user_list"))


@admin_user_bp.route("/<int:user_id>/toggle_admin", methods=["POST"])
def toggle_admin(user_id: int):
    """
    一鍵升/降級 admin（有保護：不能移除最後一個 admin）
    """
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for("admin_user.user_list"))

    if user.is_admin:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            # 最後一個 admin 不能降級
            return redirect(url_for("admin_user.user_list"))

        user.is_admin = False
    else:
        user.is_admin = True

    db.session.commit()
    return redirect(url_for("admin_user.user_list"))


@admin_user_bp.route("/<int:user_id>/delete", methods=["POST"])
def user_delete(user_id: int):
    """
    刪除會員：
    - 不能刪自己
    - 不能刪最後一個 admin
    """
    current_user_id = session.get("user_id")
    if current_user_id and int(current_user_id) == user_id:
        return redirect(url_for("admin_user.user_list"))

    user = User.query.get(user_id)
    if not user:
        return redirect(url_for("admin_user.user_list"))

    if user.is_admin:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            return redirect(url_for("admin_user.user_list"))

    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("admin_user.user_list"))
