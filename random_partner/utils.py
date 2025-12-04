import requests
import random
import json
import os
from datetime import datetime
from config import (
    ZHIPU_API_KEY, ZHIPU_API_URL, MODEL_NAME,
    TOTAL_HUMANS, ALIVE_HUMANS, REGION_RATIO, ORIENTATION_RATIO,
    CHAT_SAVE_FOLDER, PERSONALITY_PROMPT_TEMPLATE, REPLY_PROMPT_TEMPLATE
)

# ========== 原有函数保持不变 ==========
def calculate_match_probability(age: int, region: str, orientation: str) -> float:
    alive_prob = ALIVE_HUMANS / TOTAL_HUMANS
    age_prob = 0.07
    region_prob = REGION_RATIO.get(region, 1.0)
    ori_prob = ORIENTATION_RATIO.get(orientation, 1.0)
    final_prob = alive_prob * age_prob * region_prob * ori_prob
    return round(final_prob * 100, 4)

def generate_meeting_story(
    user_age: int, user_region: str,
    partner_era: str, partner_job: str
) -> str:
    prompt = f"""
    用户是{user_age}岁{user_region}人，伴侣是{partner_era}的{partner_job}。
    写1个轻松幽默的相遇场景，不超过50字，结尾加1个契合的emoji，口语化表达。
    """
    headers = {"Authorization": ZHIPU_API_KEY, "Content-Type": "application/json"}
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.85,
        "max_tokens": 100
    }
    try:
        response = requests.post(ZHIPU_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        fallback_stories = [
            f"在{partner_era}的街头，{partner_job}突然对你笑了~😆",
            f"穿越时空时偶遇{partner_job}，TA说：终于等到你！🎉",
            f"在{partner_era}的市集，你和{partner_job}抢同一个物件~🤣"
        ]
        return random.choice(fallback_stories)

def get_reject_text() -> str:
    from config import REJECT_TEXTS
    return random.choice(REJECT_TEXTS)

# ========== 新增：人物设定生成函数 ==========
def generate_partner_personality(partner_era: str, partner_job: str) -> dict:
    """生成伴侣详细人物设定（JSON格式）"""
    prompt = PERSONALITY_PROMPT_TEMPLATE.format(
        partner_era=partner_era,
        partner_job=partner_job
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
        return json.loads(result)  # 解析为JSON字典
    except Exception as e:
        # 异常兜底设定
        fallback_personality = {
            "personality": ["直率", "热情"],
            "hobbies": [f"{partner_job}相关", "探索未知"],
            "catchphrase": "很高兴认识你！",
            "speaking_style": "简短、口语化、贴合时代",
            "background": f"一位来自{partner_era}的{partner_job}，热爱生活"
        }
        return fallback_personality

# ========== 新增：聊天记录保存函数 ==========
def save_chat_history(partner_info: dict, chat_history: list):
    """
    保存聊天记录到JSON文件
    :param partner_info: 伴侣信息（含时代、职业、人物设定）
    :param chat_history: 聊天记录列表（[{role, content, time}, ...]）
    """
    # 创建保存文件夹（不存在则创建）
    if not os.path.exists(CHAT_SAVE_FOLDER):
        os.makedirs(CHAT_SAVE_FOLDER)
    
    # 生成文件名（时间戳+伴侣职业，避免重复）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_{partner_info['job']}_{timestamp}.json"
    save_path = os.path.join(CHAT_SAVE_FOLDER, filename)
    
    # 组装保存数据
    save_data = {
        "partner_info": partner_info,
        "chat_history": chat_history,
        "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 写入JSON文件（格式化输出，便于阅读）
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    
    return save_path  # 返回保存路径，给用户提示

# ========== 新增：伴侣回复生成函数 ==========
def generate_partner_reply(
    user_age: int, user_region: str,
    partner_info: dict, user_message: str
) -> str:
    """基于人物设定生成伴侣回复"""
    prompt = REPLY_PROMPT_TEMPLATE.format(
        partner_era=partner_info["era"],
        partner_job=partner_info["job"],
        personality_json=json.dumps(partner_info["personality"], ensure_ascii=False),
        user_age=user_age,
        user_region=user_region,
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
        # 兜底回复（贴合人物设定）
        catchphrase = partner_info["personality"]["catchphrase"]
        return f"{catchphrase} 你说的我记下啦~😉"