import os
import shutil
from app import create_app
from app.database import db
from app.models.product import Product
from app.models.product_image import ProductImage

app = create_app()

SEED_FOLDER = "app/static/products_seed"
TARGET_FOLDER = "app/static/products"

os.makedirs(TARGET_FOLDER, exist_ok=True)


def add_or_update_product(name, gender, season, price, stock, description, image_prefix):
    """
    - 若已存在同名 + 性別 + 季節的商品：更新資料 + 重建圖片
    - 若不存在：建立新商品 + 圖片
    不會影響其他手動建立的商品。
    """
    # 1) 試著找舊的 demo 商品
    product = Product.query.filter_by(
        name=name,
        gender=gender,
        season=season
    ).first()

    if product is None:
        # 新增 demo 商品
        product = Product(
            name=name,
            gender=gender,
            season=season,
            price=price,
            stock=stock,
            description=description,
            active=True
        )
        db.session.add(product)
        db.session.commit()
        print(f"Created product: {name}")
    else:
        # 已存在 → 更新欄位
        product.price = price
        product.stock = stock
        product.description = description
        product.active = True
        db.session.commit()
        print(f"Updated product: {name}")

    # 2) 先刪掉這個商品舊的圖片紀錄（只刪這個 product_id 的，不碰其他商品）
    ProductImage.query.filter_by(product_id=product.id).delete()
    db.session.commit()

    # 3) 複製圖片 & 建立 ProductImage
    for i in range(1, 4):
        src = f"{SEED_FOLDER}/{image_prefix}_{i}.jpg"
        if not os.path.exists(src):
            continue

        # 檔名不要含 product.id，避免每次 seed 長新檔案
        filename = f"{image_prefix}_{i}.jpg"
        dst = f"{TARGET_FOLDER}/{filename}"
        shutil.copy(src, dst)  # 若檔案已存在會被覆蓋，沒關係

        img = ProductImage(
            product_id=product.id,
            filename=filename,
            is_main=(i == 1)
        )
        db.session.add(img)

    db.session.commit()


with app.app_context():
    print("Seeding demo products (will not delete manually created products)...")

    add_or_update_product(
        name="男生白色 T-shirt",
        gender="M",
        season="summer",
        price=19.99,
        stock=100,
        description="舒適透氣的夏季白色 T-shirt。",
        image_prefix="men_tshirt_white"
    )

    add_or_update_product(
        name="男生牛仔褲",
        gender="M",
        season="fall",
        price=49.99,
        stock=80,
        description="耐穿且時尚的牛仔褲。",
        image_prefix="men_jeans"
    )

    add_or_update_product(
        name="男生外套",
        gender="M",
        season="winter",
        price=89.99,
        stock=60,
        description="保暖防風冬季外套。",
        image_prefix="men_jacket"
    )

    add_or_update_product(
        name="女生紅洋裝",
        gender="F",
        season="summer",
        price=59.99,
        stock=70,
        description="亮眼紅洋裝，適合各種場合。",
        image_prefix="women_dress_red"
    )

    add_or_update_product(
        name="女生短袖上衣",
        gender="F",
        season="spring",
        price=29.99,
        stock=90,
        description="柔軟舒適的春季短袖上衣。",
        image_prefix="women_blouse"
    )

    add_or_update_product(
        name="女生牛仔短褲",
        gender="F",
        season="summer",
        price=34.99,
        stock=110,
        description="夏季常見百搭牛仔短褲。",
        image_prefix="women_shorts"
    )

    add_or_update_product(
        name="兒童外套",
        gender="K",
        season="winter",
        price=39.99,
        stock=50,
        description="兒童冬季保暖外套。",
        image_prefix="kids_jacket"
    )

    add_or_update_product(
        name="兒童 T-shirt",
        gender="K",
        season="summer",
        price=14.99,
        stock=120,
        description="可愛舒適的兒童短袖 T-shirt。",
        image_prefix="kids_tshirt"
    )

    add_or_update_product(
        name="兒童牛仔褲",
        gender="K",
        season="fall",
        price=29.99,
        stock=100,
        description="耐穿的兒童牛仔褲。",
        image_prefix="kids_jeans"
    )

    print("Done seeding.")
