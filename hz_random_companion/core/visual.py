# core/visual.py
from config import settings
from models.companion import Companion

def get_hz_visual_config(companion: Companion) -> dict:
    """生成杭州场景+时代+情绪的视觉配置（给前端/TouchDesigner）"""
    # 基础场景视觉配置
    scene_visual = settings.HZ_SCENE_VISUAL.get(companion.hz_scene, settings.HZ_SCENE_VISUAL["west_lake"])
    # 情绪叠加配置
    emotion_overlay = {
        "happy": {"particle_count": 120, "speed": 1.5},
        "angry": {"particle_count": 150, "speed": 2.0},
        "sad": {"particle_count": 50, "speed": 0.8},
        "neutral": {"particle_count": 80, "speed": 1.0}
    }.get(companion.mood, emotion_overlay["neutral"])
    # 时代专属视觉标签
    era_tag = {
        "song": "ancient_petal",
        "republic": "old_photo",
        "modern": "glass_morphism",
        "future": "cyber_neon"
    }.get(companion.era, "normal")
    
    return {**scene_visual, **emotion_overlay, "era_tag": era_tag, "era": companion.era}