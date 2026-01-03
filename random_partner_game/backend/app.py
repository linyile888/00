from flask import Flask, request, jsonify
from .db_model import create_tables, get_db, User
from .matching_algorithm import match_partner
from .zhipu_api_service import call_zhipu_api
from .config import PARTNER_POOL
import json

# 创建Flask应用
app = Flask(__name__)

# 初始化数据库（首次运行自动创建表）
create_tables()

# 接口1：提交问卷数据并匹配伴侣
@app.route("/api/submit_survey", methods=["POST"])
def submit_survey():
    try:
        user_data = request.json
        # 验证必填字段（报错预判：前端提交数据缺失）
        required_fields = ["personality", "hobby", "age", "height", "weight", "preferred_era"]
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                return jsonify({"status": "error", "message": f"缺少必填字段：{field}"}), 400

        # 1. 存储用户数据到数据库
        db = next(get_db())
        new_user = User(
            personality=user_data["personality"],
            hobby=user_data["hobby"],
            age=user_data["age"],
            height=user_data["height"],
            weight=user_data["weight"],
            preferred_era=user_data["preferred_era"]
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # 2. 匹配伴侣
        matched_partner = match_partner(user_data)
        # 更新用户的匹配伴侣ID
        new_user.matched_partner_id = matched_partner["id"]
        db.commit()

        # 3. 返回结果给前端
        return jsonify({
            "status": "success",
            "user_id": new_user.id,
            "matched_partner": matched_partner
        })
    except Exception as e:
        # 报错预判：数据库操作失败或匹配逻辑异常
        print(f"[错误] 提交问卷失败：{str(e)}")
        return jsonify({"status": "error", "message": "提交失败，请重试！"}), 500

# 接口2：获取伴侣对话回复
@app.route("/api/get_partner_response", methods=["POST"])
def get_partner_response():
    try:
        data = request.json
        # 验证必填字段
        required_fields = ["user_input", "partner_id"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"status": "error", "message": f"缺少必填字段：{field}"}), 400

        # 获取伴侣人设
        partner = next((p for p in PARTNER_POOL if p["id"] == data["partner_id"]), None)
        if not partner:
            # 报错预判：伴侣ID不存在
            return jsonify({"status": "error", "message": "伴侣不存在！"}), 404

        # 调用智谱API生成回复
        response = call_zhipu_api(data["user_input"], partner["dialogue_style"])
        return jsonify({
            "status": "success",
            "response": response
        })
    except Exception as e:
        print(f"[错误] 获取伴侣回复失败：{str(e)}")
        return jsonify({"status": "error", "message": "获取回复失败，请重试！"}), 500

# 运行后端服务（端口5000，前端需对应此端口）
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)