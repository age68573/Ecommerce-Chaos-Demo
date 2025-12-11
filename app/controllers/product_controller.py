from flask import Blueprint, render_template, request, abort
from app.services import product_service, image_service

product_bp = Blueprint("product", __name__)

# 產品圖片專用 route（讓 chaos 可以介入）
@product_bp.route("/images/products/<filename>")
def product_image(filename):
    return image_service.serve_product_image(filename)


@product_bp.route("/products")
def product_list():
    # 從 query string 取得 gender / season，例如 ?gender=M&season=summer
    gender = request.args.get("gender") or ""
    season = request.args.get("season") or ""

    # 空字串轉回 None 給 service 使用
    products = product_service.list_products(gender or None, season or None)

    return render_template(
        "products.html",
        products=products,
        image_url=image_service.product_image_url,
        current_gender=gender,
        current_season=season,
    )


@product_bp.route("/products/<int:product_id>")
def product_detail(product_id: int):
    product = product_service.get_product_with_images(product_id)
    if not product:
        abort(404)

    # 主圖：is_main=True 的第一張，否則 images[0]
    main_image = None
    detail_images = []

    imgs = product.images
    for img in imgs:
        if img.is_main and main_image is None:
            main_image = img
        else:
            detail_images.append(img)

    if main_image is None and imgs:
        main_image = imgs[0]
        detail_images = imgs[1:]

    return render_template(
        "product_detail.html",
        product=product,
        main_image=main_image,
        detail_images=detail_images,
        image_url=image_service.product_image_url,
    )
