import requests
import json
from .config import ZHIPU_API_KEY, ZHIPU_API_BASE_URL

# 独立的智谱API调用函数（解耦，可单独测试）
def call_zhipu_api(user_input: str, partner_persona: str) -> str:
    """
    调用智谱API生成伴侣对话
    :param user_input: 用户输入的对话内容
    :param partner_persona: 伴侣人设（如："豪迈仗义的古风侠客，说话豪爽，带古风词汇"）
    :return: 伴侣的回复内容
    """
    # 构造请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ZHIPU_API_KEY}"
    }

    # 构造请求体（可改动：调整对话历史长度、温度参数控制随机性）
    data = {
        "model": "glm-4",  # 智谱默认模型，可改为glm-3-turbo（更轻量）
        "messages": [
            {
                "role": "system",
                "content": f"你现在扮演{partner_persona}，与用户进行自然对话，回复简洁（1-2句话），符合人设风格，不要暴露身份。"
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        "temperature": 0.7,  # 0-1，越高越随机
        "top_p": 0.8
    }

    try:
        # 发送请求
        response = requests.post(ZHIPU_API_BASE_URL, headers=headers, data=json.dumps(data), timeout=10)
        response.raise_for_status()  # 触发HTTP错误（如401、403）
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        # 报错预判1：网络超时
        return "哎呀，信号不好～ 等我一下再回复你呀！"
    except requests.exceptions.RequestException as e:
        # 报错预判2：API调用失败（密钥错误、网络问题等）
        error_msg = str(e)
        if "401" in error_msg:
            print("[错误] 智谱API密钥无效或已过期，请检查.env文件中的ZHIPU_API_KEY！")
        elif "403" in error_msg:
            print("[错误] 智谱API权限不足，可能是模型未开通或额度用完！")
        else:
            print(f"[错误] 智谱API调用失败：{error_msg}")
        return "我好像暂时联系不上你～ 稍后再试试吧！"
    except KeyError as e:
        # 报错预判3：API返回格式异常
        print(f"[错误] 智谱API返回数据格式错误，缺失字段：{e}")
        return "我有点混乱了，换个话题聊聊吧！"

# 测试API调用（可选，单独运行此文件验证）
if __name__ == "__main__":
    test_input = "你好呀，很高兴认识你！"
    test_persona = "豪迈仗义的古风侠客，说话豪爽，带古风词汇"
    response = call_zhipu_api(test_input, test_persona)
    print(f"伴侣回复：{response}")