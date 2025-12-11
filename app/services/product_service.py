from typing import Optional, List

from sqlalchemy import text
from app.database import db
from app.models.product import Product
from app.models.product_image import ProductImage
from app.services import chaos_service


def list_products(gender: Optional[str] = None, season: Optional[str] = None) -> List[Product]:
    """
    商品列表：
    - 正常模式：使用合理條件 + ORDER BY
    - 開啟 slow_product_list 時：使用較爛的 query 模擬慢查詢
    - 開啟 NPLUS1_IMAGES 時：刻意 N+1 查圖片
    """
    # 只挑 active = 1 的商品
    query = Product.query.filter(Product.active == True)

    if gender:
        query = query.filter(Product.gender == gender)

    if season:
        query = query.filter(Product.season == season)

    if chaos_service.is_enabled(chaos_service.SLOW_PRODUCT_LIST):
        # ====== 爛 query：模擬沒用 index、還用 LIKE、亂排序 ======
        sql = text("""
            SELECT p.*
            FROM products p
            WHERE p.active = 1
              AND LOWER(p.name) LIKE '%shirt%'   -- 模擬亂用 LIKE
            ORDER BY NEWID()                     -- 隨機排序
        """)
        result = db.session.execute(sql)
        rows = result.mappings().all()
        # 手動轉成 Product 物件（簡單版）
        ids = [r["id"] for r in rows]
        products = Product.query.filter(Product.id.in_(ids)).all()
    else:
        # ====== 正常 query ======
        products = query.order_by(Product.created_at.desc()).limit(30).all()

    # ====== N+1 圖片查詢 ======
    if chaos_service.is_enabled(chaos_service.NPLUS1_IMAGES):
        # 每個商品再個別查一次圖片，製造很多小 query
        for p in products:
            imgs = db.session.query(ProductImage).filter_by(product_id=p.id).all()
            # 為了方便 template 使用，掛在一個暫時屬性上
            p._nplus1_images = imgs
    else:
        # 正常只用 relationship
        for p in products:
            _ = p.images

    return products


def get_product_with_images(product_id: int) -> Optional[Product]:
    product = Product.query.get(product_id)
    if not product:
        return None

    # 正常情況：只用 relationship 取得圖片
    _ = product.images
    return product
