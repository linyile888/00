from api import call_zhipu_api
from logic import load_role_memory

def build_chat_messages(role_name, user_input, history_messages=None):
    """构建聊天消息（包含角色记忆）"""
    # 初始化历史消息
    history = history_messages or []
    
    # 加载角色记忆
    role_memory = load_role_memory(role_name)
    system_prompt = f"你现在扮演{role_name}，以下是你的记忆：\n{role_memory}\n请基于记忆和上下文进行回复，保持角色一致性。"
    
    # 构建消息列表
    messages = [{"role": "system", "content": system_prompt}]
    # 添加历史消息
    messages.extend(history)
    # 添加当前用户输入
    messages.append({"role": "user", "content": user_input})
    
    return messages

def get_chat_response(role_name, user_input, history_messages=None):
    """获取聊天回复"""
    messages = build_chat_messages(role_name, user_input, history_messages)
    api_response = call_zhipu_api(messages)
    return api_response.get("choices", [{}])[0].get("message", {}).get("content", "暂无回复")