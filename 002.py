import requests
import os

def call_zhipu_api(messages, model="glm-4-flash", api_key=None):
    """
    调用智谱AI API
    
    Args:
        messages: 消息列表，格式为 [{"role": "system/user/assistant", "content": "..."}, ...]
        model: 模型名称，默认为 "glm-4-flash"
        api_key: API密钥，如果为None则从环境变量ZHIPU_API_KEY读取
    
    Returns:
        API响应的JSON数据
    """
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    # 从环境变量或参数获取API密钥
    if api_key is None:
        api_key = os.getenv("ZHIPU_API_KEY")
        if api_key is None:
            raise ValueError("请设置环境变量ZHIPU_API_KEY或传入api_key参数")

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 1.0
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API调用失败: {response.status_code}, {response.text}")

# 使用示例
role_system = "你是一个学生，根据用户的问题，用学生的语气回应相对的答案"

messages = [
    {"role": "system", "content": role_system},
    {"role": "user", "content": "你好，请介绍一下自己"}
]

# 注意：请先设置环境变量 ZHIPU_API_KEY，或直接传入api_key参数
# 例如：result = call_zhipu_api(messages, api_key="your-api-key-here")
result = call_zhipu_api(messages)
print(result['choices'][0]['message']['content'])