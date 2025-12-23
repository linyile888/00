# models/companion.py
from pydantic import BaseModel
from typing import List, Optional
import uuid

class Companion(BaseModel):
    companion_id: str = str(uuid.uuid4())
    name: str
    era: str  # 时代：song/republic/modern/future
    hz_scene: str  # 杭州场景：west_lake/qian_tang/tech_city/ancient_hangzhou
    occupation: str  # 职业：poet（宋）/businessman（民国）/programmer（现代）/cyber_engineer（未来）
    occupation_feature: str  # 职业特征描述
    personality: str  # 性格：gentle/bold/creative/calm
    vroid_model_url: str  # 对应时代/职业的VRoid模型URL
    voice_style: str  # 语音风格：ancient_song/republic_mandarin/modern_hangzhou/future_cyber
    mood: str = "neutral"  # 情绪：happy/angry/sad/neutral

    class Config:
        orm_mode = True