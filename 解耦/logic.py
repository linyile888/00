import json
import os
from roles import MEMORY_FOLDER, ROLE_MEMORY_MAP

def load_role_memory(role_name):
    """加载指定角色的记忆"""
    memory_content = ""
    memory_file = ROLE_MEMORY_MAP.get(role_name)
    if not memory_file:
        return memory_content
    
    memory_path = os.path.join(MEMORY_FOLDER, memory_file)
    try:
        if os.path.exists(memory_path):
            with open(memory_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    contents = [item.get('content', '') for item in data if isinstance(item, dict) and item.get('content')]
                    memory_content = '\n'.join(contents)
                elif isinstance(data, dict):
                    memory_content = data.get('content', str(data))
                else:
                    memory_content = str(data)
    except Exception as e:
        # 静默处理记忆加载失败，不影响主流程
        pass
    return memory_content

def init_memory_folder():
    """初始化记忆文件夹（如果不存在则创建）"""
    if not os.path.exists(MEMORY_FOLDER):
        os.makedirs(MEMORY_FOLDER)