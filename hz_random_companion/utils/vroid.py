# utils/vroid.py
import requests
from typing import Dict

def parse_vroid_era_model(vroid_url: str) -> Dict:
    """解析杭州跨时代VRoid模型的外观/动画数据"""
    response = requests.head(vroid_url)
    if response.status_code == 200:
        # 模拟解析：实际用vrm-python库解析.vrm文件
        return {
            "model_era_style": vroid_url.split("/")[-2],  # 从URL提取时代风格
            "era_animations": ["idle", "talk", "era_special"],  # 时代专属动画
            "occupation_accessory": vroid_url.split("/")[-1].split(".")[0]  # 职业配饰
        }
    raise ValueError(f"VRoid模型URL无效：{vroid_url}")