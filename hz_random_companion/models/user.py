# models/user.py
from pydantic import BaseModel
from typing import List, Optional

class UserBase(BaseModel):
    username: str
    hz_scene_prefer: List[str]  # 杭州场景偏好（["west_lake", "qian_tang"]）
    era_prefer: List[str]       # 时代偏好（["song", "republic", "modern", "future"]）
    occupation_prefer: List[str]# 职业偏好（["poet", "merchant", "programmer"]）
    personality_tags: List[str] # 性格标签（["gentle", "bold", "creative"]）

class UserCreate(UserBase):
    pass

class User(UserBase):
    user_id: str
    current_companion_id: Optional[str] = None

    class Config:
        orm_mode = True
