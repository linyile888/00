import requests
import random
from config import (
    ZHIPU_API_KEY, ZHIPU_API_URL, MODEL_NAME,
    TOTAL_HUMANS, ALIVE_HUMANS, REGION_RATIO, ORIENTATION_RATIO
)

def calculate_match_probability(age: int, region: str, orientation: str) -> float:
    """
    计算随机伴侣匹配概率（核心逻辑）
    :param age: 用户年龄
    :param region: 用户选择地区
    :param orientation: 用户取向
    :return: 最终匹配概率（百分比，保留4位小数）
    """
    # 1. 存活概率（现存人口 / 人类总数）
    alive_prob = ALIVE_HUMANS / TOTAL_HUMANS
    # 2. 年龄相近概率（现存人口中±5岁占比，约7%）
    age_prob = 0.07
    # 3. 地区概率（所选地区人口占比）
    region_prob = REGION_RATIO.get(region, 1.0)
    # 4. 取向概率（所选取向人口占比）
    ori_prob = ORIENTATION_RATIO.get(orientation, 1.0)
    
    # 最终概率（叠加所有条件）
    final_prob = alive_prob * age_prob * region_prob * ori_prob
    return round(final_prob * 100, 4)

def generate_meeting_story(
    user_age: int, user_region: str,
    partner_era: str, partner_job: str
) -> str:
    """
    调用智谱API生成趣味相遇场景
    :param user_age: 用户年龄
    :param user_region: 用户地区
    :param partner_era: 伴侣时代
    :param partner_job: 伴侣职业
    :return: 相遇场景文案（50字内）
    """
    # 构建Prompt（控制长度和风格）
    prompt = f"""
    用户是{user_age}岁{user_region}人，伴侣是{partner_era}的{partner_job}。
    写1个轻松幽默的相遇场景，不超过50字，结尾加1个契合的emoji，口语化表达。
    """
    
    headers = {
        "Authorization": ZHIPU_API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.85,  # 高随机性=更多趣味
        "max_tokens": 100
    }
    
    try:
        response = requests.post(ZHIPU_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        # 异常兜底文案（避免程序崩溃）
        fallback_stories = [
            f"在{partner_era}的街头，{partner_job}突然对你笑了~😆",
            f"穿越时空时偶遇{partner_job}，TA说：终于等到你！🎉",
            f"在{partner_era}的市集，你和{partner_job}抢同一个物件~🤣"
        ]
        return random.choice(fallback_stories)

def get_reject_text() -> str:
    """获取重新匹配的吐槽文案"""
    from config import REJECT_TEXTS
    return random.choice(REJECT_TEXTS)