import requests
import json

from requests.utils import stream_decode_response_unicode

def call_zhipu_api(messages, model="glm-4-flash"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": "1732aa9845ec4ce09dca7cd10e02d209.dA36k1HPTnFk7cLU",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.5   
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API调用失败: {response.status_code}, {response.text}")


while True: 
    role_system = "你是一个疯狂的小学生，用疯狂的语气回应相对的答案，当我说要去做其他事情的时候，你就只回答说'差不多'三个字" # 表示“当条件为真时一直循环”。由于 True 永远为真，这个循环会一直运行，直到遇到 break 才会停止。
    user_input = input("请输入你要说的话:")
    messages = [
    {
      "role": "user",
      "content": role_system + user_input
    }
]
    result = call_zhipu_api(messages)
    reply=result['choices'][0]['message']['content']
    print(reply)
    if reply == '差不多':
        print("对话结束。")
        break