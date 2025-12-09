import random
from app.config import PARTNER_POOL

def calculate_match_score(player_info, partner):
    """优化后的匹配算法（保留核心权重，去掉冗余逻辑）"""
    score = 0

    # 1. 兴趣相投（30分）
    player_hobbies = set(player_info["hobbies"])
    partner_hobbies = set(partner["hobbies"])
    common_hobbies = player_hobbies & partner_hobbies
    score += min(len(common_hobbies) / len(partner_hobbies) * 30, 30) if partner_hobbies else 0

    # 2. 性格契合（25分）
    if player_info["personality_prefer"] == partner["personality"]:
        score += 25
    complementary_pairs = [("阳光开朗", "成熟稳重"), ("古灵精怪", "温柔知性")]
    if (player_info["personality_prefer"], partner["personality"]) in complementary_pairs:
        score += 10

    # 3. 相处模式（20分）
    mode_tag_map = {
        "安静陪伴": ["安静", "文艺"],
        "热闹互动": ["外向", "有趣"],
        "共同冒险": ["运动", "冒险"],
        "深度交流": ["理性", "靠谱"]
    }
    for tag in mode_tag_map.get(player_info["interaction_mode"], []):
        if tag in partner["match_tags"]:
            score += 10
            break

    # 4. 年龄匹配（10分）
    age_ranges = ["18-22", "23-26", "27-30", "31+"]
    player_age_idx = age_ranges.index(player_info["age"])
    partner_age_idx = age_ranges.index(partner["age"])
    age_diff = abs(player_age_idx - partner_age_idx)
    score += 10 if age_diff == 0 else 5 if age_diff == 1 else 0

    # 5. 身高匹配（10分）
    height_diff = abs(player_info["height"] - partner["height"])
    score += 10 if height_diff <= 10 else 5 if height_diff <= 20 else 0

    # 6. 价值观匹配（5分）
    value_tag_map = {
        "三观契合": ["三观契合"],
        "兴趣相投": ["兴趣相投"],
        "性格互补": ["性格互补"],
        "外在条件": ["外在条件"]
    }
    for tag in value_tag_map.get(player_info["core_value"], []):
        if tag in partner["match_tags"]:
            score += 5
            break

    # 随机波动（±3分）
    score += random.randint(-3, 3)
    return round(min(score, 100), 1)

def match_best_partner(player_info):
    """匹配最佳伴侣（返回Top1+匹配建议）"""
    partner_scores = [(p, calculate_match_score(player_info, p)) for p in PARTNER_POOL]
    partner_scores.sort(key=lambda x: x[1], reverse=True)
    best_partner, best_score = partner_scores[0]

    # 生成精简建议
    suggestions = []
    common_hobbies = set(player_info["hobbies"]) & set(best_partner["hobbies"])
    if best_score >= 85:
        suggestions.append("💘 天作之合！你们高度契合，赶紧开启交流吧～")
    elif best_score >= 70:
        suggestions.append("🥰 很合拍哦！多了解彼此会更默契～")
    else:
        suggestions.append("🤝 互补的关系也能擦出火花，试试从共同爱好聊起～")
    if common_hobbies:
        suggestions.append(f"✨ 你们都喜欢{','.join(common_hobbies)}，从这里开启话题吧！")

    return {"best_partner": best_partner, "best_score": best_score, "suggestions": suggestions}