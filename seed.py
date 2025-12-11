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

# 定義所有 demo 商品（包含圖片前綴）
SEED_PRODUCTS = [
    {
        "name": "男生白色 T-shirt",
        "gender": "M",
        "season": "summer",
        "price": 19.99,
        "stock": 100,
        "description": "舒適透氣的夏季白色 T-shirt。",
        "image_prefix": "men_tshirt_white",
    },
    {
        "name": "男生牛仔褲",
        "gender": "M",
        "season": "fall",
        "price": 49.99,
        "stock": 80,
        "description": "耐穿且時尚的牛仔褲。",
        "image_prefix": "men_jeans",
    },
    {
        "name": "男生外套",
        "gender": "M",
        "season": "winter",
        "price": 89.99,
        "stock": 60,
        "description": "保暖防風冬季外套。",
        "image_prefix": "men_jacket",
    },
    {
        "name": "女生紅洋裝",
        "gender": "F",
        "season": "summer",
        "price": 59.99,
        "stock": 70,
        "description": "亮眼紅洋裝，適合各種場合。",
        "image_prefix": "women_dress_red",
    },
    {
        "name": "女生短袖上衣",
        "gender": "F",
        "season": "spring",
        "price": 29.99,
        "stock": 90,
        "description": "柔軟舒適的春季短袖上衣。",
        "image_prefix": "women_blouse",
    },
    {
        "name": "女生牛仔短褲",
        "gender": "F",
        "season": "summer",
        "price": 34.99,
        "stock": 110,
        "description": "夏季常見百搭牛仔短褲。",
        "image_prefix": "women_shorts",
    },
    {
        "name": "兒童外套",
        "gender": "K",
        "season": "winter",
        "price": 39.99,
        "stock": 50,
        "description": "兒童冬季保暖外套。",
        "image_prefix": "kids_jacket",
    },
    {
        "name": "兒童 T-shirt",
        "gender": "K",
        "season": "summer",
        "price": 14.99,
        "stock": 120,
        "description": "可愛舒適的兒童短袖 T-shirt。",
        "image_prefix": "kids_tshirt",
    },
    {
        "name": "兒童牛仔褲",
        "gender": "K",
        "season": "fall",
        "price": 29.99,
        "stock": 100,
        "description": "耐穿的兒童牛仔褲。",
        "image_prefix": "kids_jeans",
    },
]


def create_seed_product(sp: dict) -> None:
    """
    建立一筆 demo 商品 + 對應圖片
    """
    product = Product(
        name=sp["name"],
        gender=sp["gender"],
        season=sp["season"],
        price=sp["price"],
        stock=sp["stock"],
        description=sp["description"],
        active=True,
    )
    db.session.add(product)
    db.session.commit()  # 拿到 product.id

    # 複製圖片 & 建立 ProductImage
    prefix = sp["image_prefix"]
    for i in range(1, 4):
        src = f"{SEED_FOLDER}/{prefix}_{i}.jpg"
        if not os.path.exists(src):
            continue

        # 檔名不包含 product.id，這樣每次 seed 只會覆蓋，不會越長越多
        filename = f"{prefix}_{i}.jpg"
        dst = os.path.join(TARGET_FOLDER, filename)
        shutil.copy(src, dst)  # 若已存在會被覆蓋

        img = ProductImage(
            product_id=product.id,
            filename=filename,
            is_main=(i == 1),
        )
        db.session.add(img)

    db.session.commit()
    print(f"Seeded product: {sp['name']}")


with app.app_context():
    print("=== Cleaning old demo products (only seed-related) ===")

    # 1. 找出所有使用 seed 圖片前綴的 ProductImage → 這些 product 一律視為 demo
    seed_prefixes = [sp["image_prefix"] for sp in SEED_PRODUCTS]
    seed_product_ids = set()

    for prefix in seed_prefixes:
        imgs = ProductImage.query.filter(
            ProductImage.filename.like(f"{prefix}_%")
        ).all()
        for img in imgs:
            seed_product_ids.add(img.product_id)

    if seed_product_ids:
        # 先刪圖片紀錄
        ProductImage.query.filter(
            ProductImage.product_id.in_(seed_product_ids)
        ).delete(synchronize_session=False)

        # 再刪 Product
        Product.query.filter(
            Product.id.in_(seed_product_ids)
        ).delete(synchronize_session=False)

        db.session.commit()
        print(f"Deleted {len(seed_product_ids)} old demo products from DB.")
    else:
        print("No existing demo products found. Nothing to delete.")

    print("=== Seeding demo products ===")
    for sp in SEED_PRODUCTS:
        create_seed_product(sp)

    print("Done seeding.")
