from flask import Blueprint, render_template, request, redirect, url_for, session

import os
from werkzeug.utils import secure_filename

from app.database import db
from app.models.product import Product
from app.models.product_image import ProductImage
from app.services import image_service
from app.services import chaos_service  # 之後如果要在新增/刪除放 chaos 可用，不用可以先不理

admin_product_bp = Blueprint("admin_product", __name__, url_prefix="/admin/products")

@admin_product_bp.before_request
def require_admin():
    user_id = session.get("user_id")
    is_admin = session.get("is_admin")
    if not user_id or not is_admin:
        # 轉去登入頁，帶 next 回來
        return redirect(url_for("auth.login", next=request.path))


@admin_product_bp.route("/")
def admin_product_list():
    """
    後台商品列表
    """
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("admin/product_list.html", products=products)


@admin_product_bp.route("/new", methods=["GET", "POST"])
def admin_product_create():
    """
    新增商品：
    - GET: 顯示表單
    - POST: 寫入 DB + 儲存圖片
    """
    if request.method == "GET":
        return render_template("admin/product_form.html")

    # ----- POST 流程 -----
    name = request.form.get("name", "").strip()
    gender = request.form.get("gender", "").strip()
    season = request.form.get("season", "").strip()
    price = request.form.get("price", "").strip()
    stock = request.form.get("stock", "").strip()
    description = request.form.get("description", "").strip()

    errors = []

    # 簡單驗證
    if not name:
        errors.append("商品名稱必填。")
    if gender not in ("M", "F", "K"):
        errors.append("性別必須是 男裝(M) / 女裝(F) / 童裝(K)。")
    if season not in ("spring", "summer", "fall", "winter"):
        errors.append("季節必須是 spring/summer/fall/winter。")

    try:
        price_value = float(price)
        if price_value < 0:
            errors.append("價格不可為負數。")
    except ValueError:
        errors.append("價格格式不正確。")

    try:
        stock_value = int(stock)
        if stock_value < 0:
            errors.append("庫存不可為負數。")
    except ValueError:
        errors.append("庫存必須是整數。")

    images = request.files.getlist("images")

    if not images or all(img.filename == "" for img in images):
        errors.append("至少上傳一張商品圖片。")

    if errors:
        return render_template(
            "admin/product_form.html",
            errors=errors,
            form_data={
                "name": name,
                "gender": gender,
                "season": season,
                "price": price,
                "stock": stock,
                "description": description,
            },
        )

    # ----- 寫入 DB -----
    product = Product(
        name=name,
        gender=gender,
        season=season,
        price=price_value,
        stock=stock_value,
        description=description,
        active=True,
    )
    db.session.add(product)
    db.session.commit()  # 先 commit 才會有 product.id

    # ----- 儲存圖片 -----
    img_dir = image_service.get_product_image_folder()
    os.makedirs(img_dir, exist_ok=True)

    index = 0
    for img in images:
        if not img.filename:
            continue
        index += 1
        filename_raw = secure_filename(img.filename)
        ext = os.path.splitext(filename_raw)[1] or ".jpg"
        filename = f"p{product.id}_{index}{ext}"

        save_path = os.path.join(img_dir, filename)
        img.save(save_path)

        pi = ProductImage(
            product_id=product.id,
            filename=filename,
            is_main=(index == 1),
        )
        db.session.add(pi)

    db.session.commit()

    return redirect(url_for("admin_product.admin_product_list"))


@admin_product_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
def admin_product_edit(product_id: int):
    """
    編輯商品資訊（不動圖片）
    """
    product = Product.query.get(product_id)
    if not product:
        return redirect(url_for("admin_product.admin_product_list"))

    if request.method == "GET":
        # 把現有資料塞進 form_data，讓表單預設值顯示
        form_data = {
            "name": product.name,
            "gender": product.gender,
            "season": product.season,
            "price": str(product.price),
            "stock": str(product.stock),
            "description": product.description or "",
        }
        return render_template(
            "admin/product_edit.html",
            form_data=form_data,
            errors=None,
            product_id=product.id,
        )

    # ----- POST：更新商品 -----
    name = request.form.get("name", "").strip()
    gender = request.form.get("gender", "").strip()
    season = request.form.get("season", "").strip()
    price = request.form.get("price", "").strip()
    stock = request.form.get("stock", "").strip()
    description = request.form.get("description", "").strip()

    errors = []

    if not name:
        errors.append("商品名稱必填。")
    if gender not in ("M", "F", "K"):
        errors.append("性別必須是 男裝(M) / 女裝(F) / 童裝(K)。")
    if season not in ("spring", "summer", "fall", "winter"):
        errors.append("季節必須是 spring/summer/fall/winter。")

    try:
        price_value = float(price)
        if price_value < 0:
            errors.append("價格不可為負數。")
    except ValueError:
        errors.append("價格格式不正確。")

    try:
        stock_value = int(stock)
        if stock_value < 0:
            errors.append("庫存不可為負數。")
    except ValueError:
        errors.append("庫存必須是整數。")

    if errors:
        form_data = {
            "name": name,
            "gender": gender,
            "season": season,
            "price": price,
            "stock": stock,
            "description": description,
        }
        return render_template(
            "admin/product_edit.html",
            form_data=form_data,
            errors=errors,
            product_id=product.id,
        )

    # 寫回 DB（不動圖片相關欄位）
    product.name = name
    product.gender = gender
    product.season = season
    product.price = price_value
    product.stock = stock_value
    product.description = description
    db.session.commit()

    return redirect(url_for("admin_product.admin_product_list"))


@admin_product_bp.route("/<int:product_id>/delete", methods=["POST"])
def admin_product_delete(product_id: int):
    """
    刪除商品：
    - 刪除 ProductImage 資料
    - 刪除對應圖片檔案（若無其他商品共用該檔案）
    - 刪除 Product
    """
    product = Product.query.get(product_id)
    if not product:
        return redirect(url_for("admin_product.admin_product_list"))

    img_dir = image_service.get_product_image_folder()

    images = ProductImage.query.filter_by(product_id=product.id).all()

    for img in images:
        same_file_count = (
            ProductImage.query
            .filter(
                ProductImage.filename == img.filename,
                ProductImage.product_id != product.id
            )
            .count()
        )

        if same_file_count == 0:
            file_path = os.path.join(img_dir, img.filename)
            try:
                os.remove(file_path)
            except FileNotFoundError:
                pass

    ProductImage.query.filter_by(product_id=product.id).delete()
    db.session.delete(product)
    db.session.commit()

    return redirect(url_for("admin_product.admin_product_list"))
