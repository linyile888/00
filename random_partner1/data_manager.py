import json
import os
from config import SAVE_PATH

def save_data(data: dict):
    """保存用户信息/交流记录到JSON"""
    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            old_data = json.load(f)
        old_data.update(data)
        data = old_data
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_data() -> dict:
    """加载JSON中的用户数据"""
    if not os.path.exists(SAVE_PATH):
        return {}
    with open(SAVE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_chat_record(user_id: str, partner_id: str, chat: dict):
    """保存单次交流记录"""
    data = load_data()
    if f"chat_{user_id}_{partner_id}" not in data:
        data[f"chat_{user_id}_{partner_id}"] = []
    data[f"chat_{user_id}_{partner_id}"].append(chat)
    save_data(data)