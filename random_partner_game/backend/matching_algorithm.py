from .config import MATCH_WEIGHTS, PARTNER_POOL
from typing import Dict, List

# 独立的匹配逻辑（解耦，可单独修改算法）
def calculate_similarity(user_data: Dict, partner_data: Dict) -> float:
    """
    计算用户与伴侣的相似度得分（0-1）
    :param user_data: 用户问卷数据
    :param partner_data: 伴侣数据
    :return: 相似度得分
    """
    total_score = 0.0

    # 1. 性格相似度（字符串匹配，简单版：是否包含相同关键词）
    user_personality = user_data["personality"].lower()
    partner_personality = partner_data["personality"].lower()
    personality_keywords = ["开朗", "内向", "温柔", "豪迈", "理性", "感性"]
    match_count = sum(1 for kw in personality_keywords if kw in user_personality and kw in partner_personality)
    personality_score = match_count / len(personality_keywords) if personality_keywords else 1.0

    # 2. 喜好相似度（同上，关键词匹配）
    user_hobby = user_data["hobby"].lower()
    partner_hobby = partner_data["hobby"].lower()
    hobby_keywords = ["游戏", "读书", "运动", "音乐", "旅行", "美食", "编程", "艺术"]
    hobby_match_count = sum(1 for kw in hobby_keywords if kw in user_hobby and kw in partner_hobby)
    hobby_score = hobby_match_count / len(hobby_keywords) if hobby_keywords else 1.0

    # 3. 年龄相似度（归一化到0-1，差距越小得分越高）
    age_diff = abs(user_data["age"] - partner_data["age"])
    age_score = max(0, 1 - age_diff / 20)  # 年龄差距超过20分则得0分

    # 4. 身高相似度（归一化到0-1）
    height_diff = abs(user_data["height"] - partner_data["height"])
    height_score = max(0, 1 - height_diff / 30)  # 身高差距超过30cm得0分

    # 5. 体重相似度（归一化到0-1）
    weight_diff = abs(user_data["weight"] - partner_data["weight"])
    weight_score = max(0, 1 - weight_diff / 20)  # 体重差距超过20kg得0分

    # 6. 时代偏好相似度（完全匹配得1分，否则0分）
    era_score = 1.0 if user_data["preferred_era"] == partner_data["era"] else 0.3

    # 加权求和（按配置的权重）
    total_score = (
        personality_score * MATCH_WEIGHTS["personality"]
        + hobby_score * MATCH_WEIGHTS["hobby"]
        + age_score * MATCH_WEIGHTS["age"]
        + height_score * MATCH_WEIGHTS["height"]
        + weight_score * MATCH_WEIGHTS["weight"]
        + era_score * MATCH_WEIGHTS["era"]
    )

    return round(total_score, 2)

def match_partner(user_data: Dict) -> Dict:
    """
    为用户匹配最优伴侣（相似度最高+随机筛选，避免重复）
    :param user_data: 用户问卷数据
    :return: 匹配的伴侣数据
    """
    # 计算所有伴侣的相似度
    partner_scores = []
    for partner in PARTNER_POOL:
        score = calculate_similarity(user_data, partner)
        partner_scores.append((partner, score))

    # 筛选相似度前3的伴侣，再随机选择1个（增加随机性）
    top_partners = sorted(partner_scores, key=lambda x: x[1], reverse=True)[:3]
    import random
    matched_partner, match_score = random.choice(top_partners)

    # 添加匹配得分（可选，用于前端展示）
    matched_partner["match_score"] = match_score
    return matched_partner

# 测试匹配算法（可选，单独运行此文件验证）
if __name__ == "__main__":
    test_user_data = {
        "personality": "开朗乐观",
        "hobby": "游戏、旅行、美食",
        "age": 24,
        "height": 175,
        "weight": 65,
        "preferred_era": "未来"
    }
    matched = match_partner(test_user_data)
    print(f"匹配结果：{matched['name']}（相似度：{matched['match_score']}）")
    print(f"伴侣信息：{matched}")