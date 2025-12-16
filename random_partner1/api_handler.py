import requests
import json
import streamlit as st
import os  # 新增：导入os模块读取环境变量

def call_zhipu_api(prompt: str, model: str = "glm-4") -> str:
    """调用智谱API生成内容（人物设定/对话）"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    # 核心修复：先读Secrets，失败则读环境变量
    try:
        api_key = st.secrets["ZHI_PU_API_KEY"]
    except KeyError:
        api_key = os.getenv("ZHI_PU_API_KEY")  # 从环境变量读取
        if not api_key:
            return "错误：未配置智谱API Key！请在secrets.toml或环境变量中设置ZHI_PU_API_KEY"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"  # 使用读取到的API Key
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API调用失败：{str(e)}"

def generate_partner_profile(preferences: dict) -> str:
    """生成伴侣人物设定"""
    prompt = f"""根据用户偏好生成随机知心伴侣的人物设定，要求包含：
    1. 基本信息（性别、年龄、身高、体重、地区）
    2. 性格、爱好、职业
    3. 与用户的匹配点
    用户偏好：{json.dumps(preferences, ensure_ascii=False)}
    输出格式：简洁的人物卡片，口语化表述。"""
    return call_zhipu_api(prompt)

def generate_chat_response(partner_profile: str, user_input: str) -> str:
    """生成伴侣的对话回复"""
    prompt = f"""你是用户的随机知心伴侣，人物设定：{partner_profile}
    用户对你说：{user_input}
    请以伴侣的身份回复，语气贴合人物设定，字数50-100字。"""
    return call_zhipu_api(prompt)