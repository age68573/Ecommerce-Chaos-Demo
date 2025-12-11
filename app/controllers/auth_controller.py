from flask import Blueprint, render_template, request, redirect, url_for, session
from app.services import auth_service
from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html", errors=None)

    username_or_email = request.form.get("username_or_email", "").strip()
    password = request.form.get("password", "").strip()

    errors = []
    user = auth_service.authenticate(username_or_email, password)
    if not user:
        errors.append("帳號或密碼錯誤。")

    if errors:
        return render_template("auth/login.html", errors=errors)

    # 登入成功 → 寫入 session
    session["user_id"] = user.id
    session["is_admin"] = bool(user.is_admin)

    next_url = request.args.get("next") or url_for("home.home")
    return redirect(next_url)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home.home"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    簡單會員註冊（一般使用者，非 admin）
    """
    if request.method == "GET":
        return render_template("auth/register.html", errors=None, form_data=None)

    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    password2 = request.form.get("password2", "").strip()

    errors = []
    if not username:
        errors.append("使用者名稱必填。")
    if not email:
        errors.append("Email 必填。")
    if not password:
        errors.append("密碼必填。")
    if password != password2:
        errors.append("兩次輸入的密碼不一致。")

    if User.query.filter_by(username=username).first():
        errors.append("此使用者名稱已被註冊。")
    if User.query.filter_by(email=email).first():
        errors.append("此 Email 已被註冊。")

    if errors:
        return render_template(
            "auth/register.html",
            errors=errors,
            form_data={"username": username, "email": email},
        )

    auth_service.create_user(username=username, email=email, password=password, is_admin=False)
    return redirect(url_for("auth.login"))
