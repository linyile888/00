import json
import os
from app.config import PLAYER_DATA_PATH, PARTNER_DATA_PATH, CHAT_RECORD_PATH

def init_data_file(path):
    """初始化JSON文件（不存在则创建空列表）"""
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def load_data(path):
    """读取JSON数据"""
    init_data_file(path)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data, path):
    """保存数据到JSON文件"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_player_info(player_info):
    """保存玩家信息并返回player_id"""
    players = load_data(PLAYER_DATA_PATH)
    player_id = len(players) + 1
    player_info["player_id"] = player_id
    players.append(player_info)
    save_data(players, PLAYER_DATA_PATH)
    return player_id

def save_partner_info(partner, player_id):
    """保存伴侣信息（关联玩家ID）"""
    partners = load_data(PARTNER_DATA_PATH)
    partner["player_id"] = player_id
    partners.append(partner)
    save_data(partners, PARTNER_DATA_PATH)

def save_chat_record(player_id, player_msg, partner_msg, partner_name):
    """保存聊天记录"""
    from datetime import datetime
    records = load_data(CHAT_RECORD_PATH)
    record = {
        "player_id": player_id,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "player_msg": player_msg,
        "partner_msg": partner_msg,
        "partner_name": partner_name
    }
    records.append(record)
    save_data(records, CHAT_RECORD_PATH)
    return record

def get_player_info(player_id):
    """根据player_id获取玩家信息"""
    players = load_data(PLAYER_DATA_PATH)
    return next((p for p in players if p["player_id"] == player_id), None)

def get_partner_info(player_id):
    """根据player_id获取伴侣信息"""
    partners = load_data(PARTNER_DATA_PATH)
    return next((p for p in partners if p["player_id"] == player_id), None)

def get_chat_records(player_id):
    """根据player_id获取聊天记录"""
    records = load_data(CHAT_RECORD_PATH)
    return [r for r in records if r["player_id"] == player_id]