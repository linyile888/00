import requests
import json
import streamlit as st  # 新增：导入streamlit读取secrets

def call_zhipu_api(prompt: str, model: str = "glm-4") -> str:
    """调用智谱API生成内容（人物设定/对话）"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Content-Type": "application/json",
        # 变更：从secrets读取API Key，替代硬编码
        "Authorization": f"Bearer {st.secrets['ZHI_PU_API_KEY']}"
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
    # 变更：移除硬编码api_key，使用函数默认的secrets读取逻辑
    return call_zhipu_api(prompt)

def generate_chat_response(partner_profile: str, user_input: str) -> str:
    """生成伴侣的对话回复"""
    prompt = f"""你是用户的随机知心伴侣，人物设定：{partner_profile}
    用户对你说：{user_input}
    请以伴侣的身份回复，语气贴合人物设定，字数50-100字。"""
    # 变更：移除硬编码api_key，使用函数默认的secrets读取逻辑
    return call_zhipu_api(prompt)