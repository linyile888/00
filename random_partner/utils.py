import requests
import random
import json
import os
from datetime import datetime
from config import (
    ZHIPU_API_KEY, ZHIPU_API_URL, MODEL_NAME,
    TOTAL_HUMANS, ALIVE_HUMANS, REGION_RATIO, ORIENTATION_RATIO,
    CHAT_SAVE_FOLDER, PERSONALITY_PROMPT_TEMPLATE, REPLY_PROMPT_TEMPLATE,
    PARTNER_PERSONALITY_TYPES, PARTNER_HOBBIES_TYPES
)

# ========== 优化：概率计算（加入偏好契合度） ==========
def calculate_match_probability(
    user_info: dict, user_preferences: dict
) -> tuple[float, float]:
    """
    计算匹配概率（含基础概率+偏好契合度）
    :param user_info: 玩家基本信息（age, gender, height, weight）
    :param user_preferences: 玩家偏好（region, orientation, personality, hobbies）
    :return: (基础概率, 偏好契合度, 最终概率)
    """
    # 1. 基础概率计算（原有逻辑）
    alive_prob = ALIVE_HUMANS / TOTAL_HUMANS
    age_prob = 0.07
    region_prob = REGION_RATIO.get(user_preferences["region"], 1.0)
    ori_prob = ORIENTATION_RATIO.get(user_preferences["orientation"], 1.0)
    base_prob = alive_prob * age_prob * region_prob * ori_prob * 100  # 转百分比
    
    # 2. 偏好契合度计算（0-100分）
    personality_match = 80 if user_preferences["personality"] in PARTNER_PERSONALITY_TYPES else 50
    hobbies_match = len(set(user_preferences["hobbies"]) & set(PARTNER_HOBBIES_TYPES)) / len(user_preferences["hobbies"]) * 100 if user_preferences["hobbies"] else 60
    preference_fit = (personality_match + hobbies_match) / 2  # 平均得分
    
    # 3. 最终概率（基础概率 * 偏好契合度系数）
    final_prob = round(base_prob * (preference_fit / 100), 4)
    return round(base_prob, 4), round(preference_fit, 1), final_prob

# ========== 优化：相遇场景生成（结合玩家信息） ==========
def generate_meeting_story(
    user_info: dict, user_preferences: dict,
    partner_era: str, partner_job: str, partner_personality: str
) -> str:
    """生成相遇场景（融入玩家爱好和伴侣性格）"""
    user_hobbies = ", ".join(user_preferences["hobbies"]) if user_preferences["hobbies"] else "探索未知"
    prompt = f"""
    玩家信息：{user_info['gender']}，{user_info['age']}岁，喜欢{user_hobbies}。
    伴侣：{partner_era}的{partner_job}，性格{partner_personality}。
    写1个轻松幽默的相遇场景，突出两人爱好/性格契合点，不超过60字，结尾加1个emoji。
    """
    headers = {"Authorization": ZHIPU_API_KEY, "Content-Type": "application/json"}
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.85,
        "max_tokens": 120
    }
    try:
        response = requests.post(ZHIPU_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        fallback_stories = [
            f"你在{partner_era}的郊外{user_hobbies}，偶遇{partner_job}，TA笑着向你走来~😆",
            f"穿越时空时，同样喜欢{user_hobbies}的{partner_job}主动和你搭话！🎉",
            f"在{partner_era}的市集，你和{partner_job}因{user_hobbies}结缘，相谈甚欢~🤣"
        ]
        return random.choice(fallback_stories)

# ========== 优化：伴侣人物设定（严格匹配玩家偏好） ==========
def generate_partner_personality(
    partner_era: str, partner_job: str, user_preferences: dict
) -> tuple[dict, str, list]:
    """生成伴侣设定（契合玩家偏好）"""
    target_personality = user_preferences["personality"]
    target_hobbies = ", ".join(user_preferences["hobbies"]) if user_preferences["hobbies"] else "户外探险"
    
    prompt = PERSONALITY_PROMPT_TEMPLATE.format(
        partner_era=partner_era,
        partner_job=partner_job,
        target_personality=target_personality,
        target_hobbies=target_hobbies
    )
    headers = {"Authorization": ZHIPU_API_KEY, "Content-Type": "application/json"}
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 200
    }
    try:
        response = requests.post(ZHIPU_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()["choices"][0]["message"]["content"].strip()
        personality = json.loads(result)
        return personality, target_personality, user_preferences["hobbies"]
    except Exception as e:
        # 兜底设定（契合偏好）
        fallback_personality = {
            "personality": [target_personality, "热情"],
            "hobbies": [user_preferences["hobbies"][0] if user_preferences["hobbies"] else "探索", f"{partner_job}相关"],
            "catchphrase": "很高兴认识你！",
            "speaking_style": f"{target_personality}、简短、口语化",
            "background": f"一位来自{partner_era}的{partner_job}，热爱{target_hobbies}"
        }
        return fallback_personality, target_personality, user_preferences["hobbies"]

# ========== 新增：生成匹配建议（基于玩家与伴侣契合点） ==========
def generate_match_suggestion(
    user_info: dict, user_preferences: dict,
    partner_info: dict
) -> str:
    """生成个性化匹配建议"""
    user_hobbies = ", ".join(user_preferences["hobbies"]) if user_preferences["hobbies"] else "日常休闲"
    partner_hobbies = ", ".join(partner_info["personality"]["hobbies"])
    common_hobbies = set(user_preferences["hobbies"]) & set(partner_info["personality"]["hobbies"])
    common_text = f"你们都喜欢{', '.join(common_hobbies)}" if common_hobbies else "你们的爱好各有特色"
    
    prompt = f"""
    玩家：{user_info['gender']}，{user_info['age']}岁，喜欢{user_hobbies}，偏好{user_preferences['personality']}的伴侣。
    伴侣：{partner_info['era']}的{partner_info['job']}，性格{partner_info['target_personality']}，喜欢{partner_hobbies}。
    {common_text}，生成1条简短温馨的匹配建议，不超过50字，口语化。
    """
    headers = {"Authorization": ZHIPU_API_KEY, "Content-Type": "application/json"}
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 100
    }
    try:
        response = requests.post(ZHIPU_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"{common_text}，不妨多聊聊彼此的爱好，感情会快速升温～😉"

# ========== 原有函数保持不变（get_reject_text、save_chat_history） ==========
def get_reject_text() -> str:
    from config import REJECT_TEXTS
    return random.choice(REJECT_TEXTS)

def save_chat_history(partner_info: dict, user_info: dict, chat_history: list):
    """保存聊天记录（新增玩家信息）"""
    if not os.path.exists(CHAT_SAVE_FOLDER):
        os.makedirs(CHAT_SAVE_FOLDER)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_{partner_info['job']}_{timestamp}.json"
    save_path = os.path.join(CHAT_SAVE_FOLDER, filename)
    
    save_data = {
        "user_info": user_info,
        "partner_info": partner_info,
        "chat_history": chat_history,
        "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    
    return save_path

# ========== 优化：伴侣回复（结合玩家完整信息） ==========
def generate_partner_reply(
    user_info: dict, user_preferences: dict,
    partner_info: dict, user_message: str
) -> str:
    """基于玩家信息和伴侣设定生成回复"""
    prompt = REPLY_PROMPT_TEMPLATE.format(
        partner_era=partner_info["era"],
        partner_job=partner_info["job"],
        personality_json=json.dumps(partner_info["personality"], ensure_ascii=False),
        user_gender=user_info["gender"],
        user_age=user_info["age"],
        user_height=user_info["height"],
        user_weight=user_info["weight"],
        user_hobbies=", ".join(user_preferences["hobbies"]) if user_preferences["hobbies"] else "探索未知",
        user_message=user_message
    )
    headers = {"Authorization": ZHIPU_API_KEY, "Content-Type": "application/json"}
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
        "max_tokens": 100
    }
    try:
        response = requests.post(ZHIPU_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        catchphrase = partner_info["personality"]["catchphrase"]
        return f"{catchphrase} 你说的我记下啦~😉"