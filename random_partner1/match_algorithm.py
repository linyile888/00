import random
from config import REGION_RATIO, HEIGHT_RANGE, WEIGHT_RANGE

def calculate_match_probability(user_info: dict, preferences: dict) -> float:
    """计算匹配概率（结合人口统计+用户偏好）"""
    # 基础概率：全球约5亿潜在伴侣/70亿人口 = 1/14 ≈ 7%
    base_prob = 1 / 14
    # 地区权重
    region_weight = REGION_RATIO.get(preferences.get("region", "亚洲"), 0.6)
    # 年龄匹配权重（用户年龄±5岁为高匹配）
    age_diff = abs(user_info.get("age", 25) - preferences.get("partner_age", 25))
    age_weight = 1 - (age_diff / 20) if age_diff <= 20 else 0.1
    # 综合概率
    final_prob = base_prob * region_weight * age_weight
    return round(final_prob * 100, 4)  # 转为百分比，保留4位小数

def generate_partner_id() -> str:
    """生成唯一伴侣ID"""
    return f"partner_{random.randint(10000, 99999)}"