import os
import time
from flask import current_app, send_from_directory, abort
from app.services import chaos_service


def product_image_url(filename: str) -> str:
    """
    給 template 用的圖片 URL，統一走 /images/products/<filename>
    這樣我們就不直接用 /static，而是由 Flask route 來套 chaos。
    """
    return f"/images/products/{filename}"


def serve_product_image(filename: str):
    """
    真正送出圖片的地方，可以注入各種 chaos：
    - 慢載入
    - 404
    - 500（權限）
    """
    img_dir = current_app.config["PRODUCT_IMAGE_FOLDER"]

    if chaos_service.is_enabled(chaos_service.IMAGE_PERMISSION):
        # 模擬檔案系統錯誤
        raise PermissionError("Simulated permission error for product images")

    if chaos_service.is_enabled(chaos_service.BROKEN_IMAGES):
        # 全部回 404
        abort(404)

    if chaos_service.is_enabled(chaos_service.SLOW_IMAGES):
        # 模擬慢 IO
        time.sleep(3)

    if not os.path.exists(os.path.join(img_dir, filename)):
        abort(404)

    return send_from_directory(img_dir, filename)
