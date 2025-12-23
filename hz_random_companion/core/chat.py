# core/chat.py
from models.companion import Companion
from utils.zhipu_ai import generate_era_chat
from core.matching import HZ_COMPANION_DB

def handle_hz_chat(
    user_id: str,
    companion_id: str,
    user_input: str,
    chat_history: list = None
) -> tuple[str, str]:
    """处理杭州跨时代的对话交互"""
    companion = next((c for c in HZ_COMPANION_DB if c.companion_id == companion_id), None)
    if not companion:
        raise ValueError("杭州伴侣不存在")
    
    # 生成带时代/职业风格的回复+情绪
    reply, mood = generate_era_chat(
        user_input,
        companion.era,
        companion.occupation,
        chat_history
    )
    companion.mood = mood
    return reply, mood

