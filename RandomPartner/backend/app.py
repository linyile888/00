from flask import Flask, request, jsonify
from flask_cors import CORS
from config import config
import requests

app = Flask(__name__)
CORS(app)

# 预设伴侣数据（不用改）
PRESET_PARTNERS = [
    {"partner_id": "p1", "name": "林间侠客", "personality": "豪爽", "hobby": ["剑术", "采药"], "era": "古代", "job": "侠客", "sprite_url": "/assets/sprites/knight.png", "bg_url": "/assets/scenes/forest.png"},
    {"partner_id": "p2", "name": "星空宇航员", "personality": "冷静", "hobby": ["天文", "编程"], "era": "未来", "job": "宇航员", "sprite_url": "/assets/sprites/astronaut.png", "bg_url": "/assets/scenes/space.png"}
]

# 匹配接口
@app.route("/api/match", methods=["POST"])
def match():
    data = request.json
    # 简单匹配：选第一个伴侣（简化逻辑）
    best_partner = PRESET_PARTNERS[0]
    return jsonify({"code":200, "data":{"partner_info":best_partner, "match_score":0.9, "match_reason":"缘分天定！"}})

# 对话接口
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    partner = data["partner_info"]
    user_msg = data["user_message"]
    # 调用智谱API
    headers = {"Content-Type":"application/json", "Authorization":f"Bearer {config.ZHIPU_API_KEY}"}
    payload = {
        "model":"glm-4",
        "messages":[
            {"role":"system", f"content":"你是{partner['name']}，性格{partner['personality']}，说话简短亲切，不超过30字"},
            {"role":"user", "content":user_msg}
        ]
    }
    res = requests.post(config.ZHIPU_API_URL, headers=headers, json=payload).json()
    return jsonify({"code":200, "data":{"response":res["choices"][0]["message"]["content"]}})

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=True)