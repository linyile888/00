# app.py （Windows专属适配，智谱API已填入，完整代码无省略，直接复制即用）
from flask import Flask, request, jsonify
import sqlite3
import os
import zhipuai
from db import DB_PATH
import socket
from dotenv import load_dotenv

# 优先从 .env 加载 ZHIPU_API_KEY，若未设置则回退到硬编码（减少意外泄露风险建议删除硬编码）
load_dotenv()
# 从环境变量获取 API Key；若未配置则不启用外部智谱调用，使用本地回退逻辑
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
if ZHIPU_API_KEY:
    zhipuai.api_key = ZHIPU_API_KEY
    USE_ZHIPU = True
else:
    USE_ZHIPU = False

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 解决中文乱码，必须保留
app.config['JSON_SORT_KEYS'] = False # Windows下防止json字段乱序，必须保留

# Windows专属：自动获取本机IP，无需手动查询，避免填错，必须保留
def get_windows_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
LOCAL_IP = get_windows_ip()

# 1. 接收用户问卷数据接口（完整校验，无省略）
@app.route("/submit_user_info", methods=["POST"])
def submit_user_info():
    try:
        data = request.get_json()
        # 校验必填字段（缺一不可，完整校验无省略）
        required = ["age", "height", "weight", "personality", "hobby"]
        for key in required:
            if key not in data:
                return jsonify({"code": -1, "msg": f"缺少字段：{key}"}), 400
        # 存入数据库，完整操作无省略
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_info (age, height, weight, personality, hobby) VALUES (?,?,?,?,?)",
            (data["age"], data["height"], data["weight"], data["personality"], data["hobby"])
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return jsonify({"code": 0, "msg": "提交成功", "user_id": user_id}), 200
    except Exception as e:
        return jsonify({"code": -2, "msg": f"提交失败：{str(e)}"}), 500

# 2. 匹配伴侣核心算法（加权相似度匹配，完整逻辑无省略，无需改动）
def match_partner(user_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM partner_lib")
    partners = cursor.fetchall()
    conn.close()
    
    best_match = None
    max_score = 0
    # 加权规则（固定权重，完整无省略，想调整可改数字）
    weight = {"age": 0.2, "personality": 0.4, "hobby": 0.3, "height": 0.1}
    
    for p in partners:
        p_id, era, occ, p_age, p_h, p_w, p_per, p_hob, p_style = p
        score = 0
        # 年龄相似度（差值越小分越高，完整计算无省略）
        age_diff = abs(int(user_data["age"]) - p_age)
        score += weight["age"] * (10 - min(age_diff, 10)) / 10
        # 性格相似度（包含关键词即加分，完整判断无省略）
        if any(word in p_per for word in user_data["personality"].split(",")):
            score += weight["personality"]
        # 喜好相似度（包含关键词即加分，完整判断无省略）
        if any(word in p_hob for word in user_data["hobby"].split(",")):
            score += weight["hobby"]
        # 身高相似度（差值越小分越高，完整计算无省略）
        h_diff = abs(int(user_data["height"]) - p_h)
        score += weight["height"] * (20 - min(h_diff, 20)) / 20
        
        if score > max_score:
            max_score = score
            best_match = {
                "partner_id": p_id,
                "era": era,
                "occupation": occ,
                "age": p_age,
                "height": p_h,
                "weight": p_w,
                "personality": p_per,
                "hobby": p_hob,
                "style": p_style
            }
    return best_match

# 3. 匹配伴侣+智谱API补充人设接口（API已调用，完整逻辑无省略）
@app.route("/match_partner", methods=["POST"])
def get_match():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"code": -1, "msg": "缺少user_id"}), 400
        
        # 获取用户数据，完整查询无省略
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_info WHERE user_id=?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        if not user:
            return jsonify({"code": -2, "msg": "用户不存在"}), 404
        
        user_data = {
            "age": user[1], "height": user[2], "weight": user[3],
            "personality": user[4], "hobby": user[5]
        }
        # 基础匹配，完整调用无省略
        base_partner = match_partner(user_data)
        if not base_partner:
            return jsonify({"code": -3, "msg": "暂无匹配伴侣"}), 500
        
        # 智谱API补充伴侣细节（已填入密钥，完整prompt无省略）
        prompt = f"""
        你是随机伴侣生成助手，帮我补充这个伴侣的30字内人设简介和2句相遇问候语，要求贴合设定：
        时代：{base_partner['era']}，职业：{base_partner['occupation']}，性格：{base_partner['personality']}，风格：{base_partner['style']}
        简介要简洁有画面感，问候语符合性格，不要OOC。
        输出格式：简介|问候语1|问候语2
        """
        # 调用智谱API（优先使用；若未配置或 SDK 不可用则回退为本地简单生成）
        try:
            if USE_ZHIPU and hasattr(zhipuai, 'model_api'):
                response = zhipuai.model_api.invoke(
                    model="glm-3-turbo",
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=200,
                    top_p=0.9
                )
                res_content = response["data"]["choices"][0]["content"].strip()
                intro, greet1, greet2 = res_content.split("|")
            else:
                # 回退逻辑：本地生成简短人设和问候
                intro = f"{base_partner['style']}的{base_partner['occupation']}，性格{base_partner['personality']}。"
                greet1 = f"你好，我是{base_partner['occupation']}，很高兴认识你。"
                greet2 = f"希望一起分享{base_partner['hobby']}的快乐。"
        except AttributeError:
            # SDK 不存在 model_api 时的回退
            intro = f"{base_partner['style']}的{base_partner['occupation']}，性格{base_partner['personality']}。"
            greet1 = f"你好，我是{base_partner['occupation']}，很高兴认识你。"
            greet2 = f"希望一起分享{base_partner['hobby']}的快乐。"
        except Exception as e:
            return jsonify({"code": -4, "msg": f"智谱API调用失败：{str(e)}"}), 500
        base_partner["intro"] = intro
        base_partner["greet"] = [greet1, greet2]
        
        return jsonify({"code": 0, "msg": "匹配成功", "data": base_partner}), 200
    except Exception as e:
        return jsonify({"code": -4, "msg": f"匹配失败：{str(e)}"}), 500

# 启动服务（Windows专属配置，完整无省略，无需改动）
if __name__ == "__main__":
    print(f"Windows本机IP：{LOCAL_IP}，服务将运行在 http://{LOCAL_IP}:5000")
    print("温馨提示：Windows防火墙会弹窗，务必点击【允许访问】！")
    # host=0.0.0.0局域网可访问，threaded=True解决Windows并发，完整配置无省略
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)