from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

from app.database import db
from app.models.product import Product
from app.models.product_image import ProductImage
from app.services import image_service

admin_product_bp = Blueprint("admin_product", __name__, url_prefix="/admin/products")


@admin_product_bp.route("/")
def admin_product_list():
    """
    簡單列出所有商品，之後可以再加編輯 / 下架功能。
    先做一個入口可以確認新增成功。
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
        # 直接回傳表單 + 錯誤資訊
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
        # 為了避免檔名衝突，組一個獨特檔名
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
