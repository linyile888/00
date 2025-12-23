# utils/zhipu_ai.py
from zhipuai import ZhipuAI
from config import settings

client = ZhipuAI(api_key=settings.ZHIPU_API_KEY)

def generate_era_chat(
    user_input: str,
    companion_era: str,
    companion_occupation: str,
    chat_history: list = None
) -> tuple[str, str]:
    """生成带时代/职业风格的AI回复，同时识别情绪"""
    chat_history = chat_history or []
    # 时代+职业的prompt定制（杭州地域化）
    era_occupation_prompt = {
        "song_poet": "你是南宋杭州的诗人，说话带宋词意境，用词婉约，提及西湖、苏堤等杭州地标，语气温柔。",
        "republic_businessman": "你是民国杭州的商人，说话带老杭州话腔，提及清河坊、湖滨商圈，语气干练。",
        "modern_programmer": "你是杭州未来科技城的程序员，说话带互联网黑话，提及阿里、云栖大会，语气轻松。",
        "future_cyber_engineer": "你是未来杭州的赛博工程师，说话带霓虹科技感，提及钱塘数字城、元宇宙西湖，语气冷峻。"
    }.get(f"{companion_era}_{companion_occupation}", "你是杭州的普通人，说话带杭州方言尾音，语气自然。")
    
    messages = [
        {"role": "system", "content": era_occupation_prompt},
        *chat_history,
        {"role": "user", "content": user_input}
    ]
    
    # 调用智谱AI
    response = client.chat.completions.create(
        model=settings.ZHIPU_MODEL,
        messages=messages,
        temperature=0.8
    )
    reply = response.choices[0].message.content.strip()
    
    # 情绪识别（简化版）
    mood = "neutral"
    if "开心" in reply or "喜" in reply or "哈哈" in reply:
        mood = "happy"
    elif "生气" in reply or "怒" in reply:
        mood = "angry"
    elif "难过" in reply or "悲" in reply:
        mood = "sad"
    
    return reply, mood
