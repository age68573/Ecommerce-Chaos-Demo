from app.models.chaos_config import ChaosConfig


# 定義一些我們會用到的 chaos key
SLOW_PRODUCT_LIST = "slow_product_list"
NPLUS1_IMAGES     = "nplus1_images"
SLOW_IMAGES       = "slow_images"
BROKEN_IMAGES     = "broken_images"
IMAGE_PERMISSION  = "image_permission_error"


def is_enabled(key: str) -> bool:
    return ChaosConfig.get_bool(key, default=False)


def set_flag(key: str, flag: bool):
    ChaosConfig.set_bool(key, flag)
