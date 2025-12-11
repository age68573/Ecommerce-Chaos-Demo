import os
from urllib.parse import quote_plus  # 加這行

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")

    # ===== MSSQL via SQLAlchemy + pytds =====
    MSSQL_HOST = os.environ.get("MSSQL_HOST", "10.107.85.88")
    MSSQL_PORT = int(os.environ.get("MSSQL_PORT", "1433"))
    MSSQL_DB   = os.environ.get("MSSQL_DB", "EcommerceChaosDemo")
    MSSQL_USER = os.environ.get("MSSQL_USER", "sa")
    MSSQL_PWD  = os.environ.get("MSSQL_PWD", "P@ssw0rd")
    MSSQL_PWD_RAW  = os.environ.get("MSSQL_PWD", "P@ssw0rd")

    # 這裡非常重要：把 @ 做 URL encode
    MSSQL_PWD = quote_plus(MSSQL_PWD_RAW)

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pymssql://{MSSQL_USER}:{MSSQL_PWD}"
        f"@{MSSQL_HOST}:{MSSQL_PORT}/{MSSQL_DB}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 靜態圖片資料夾（給 image_service 用）
    PRODUCT_IMAGE_FOLDER = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "app", "static", "products"
    )
