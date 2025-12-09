from zhipuai import ZhipuAI
from app.config import ZHIPU_API_KEY, ZHIPU_MODEL

def generate_partner_reply(player_msg, player_info, partner_info):
    """
    精简核心提示词：只保留人设、玩家信息、对话要求，去掉所有冗余描述
    """
    client = ZhipuAI(api_key=ZHIPU_API_KEY)

    # 核心提示词（仅保留必要信息）
    prompt = f"""
    角色：{partner_info['name']}，{partner_info['personality']}，{partner_info['background']}，爱好{','.join(partner_info['hobbies'])}。
    玩家：{player_info['gender']}，{player_info['age']}，爱好{','.join(player_info['hobbies'])}，喜欢{player_info['interaction_mode']}相处。
    场景：刚匹配的伴侣，轻松自然聊天，带一个小互动引导继续对话。
    玩家消息：{player_msg}
    要求：30-50字，符合角色性格，不暴露扮演身份。
    """

    response = client.chat.completions.create(
        model=ZHIPU_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=100,
        top_p=0.9
    )
    return response.choices[0].message.content.strip()