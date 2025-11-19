import requests
import json
import webbrowser
import threading
import time
import http.server
import socketserver
import os
import qrcode
from requests.utils import stream_decode_response_unicode

# ========== 核心配置 ==========
PORT = 8080  # 本地服务端口
LOCAL_URL = f"http://127.0.0.1:{PORT}"
TEMP_HTML_FILE = "design_mystery_game.html"  # 生成的游戏网页文件
NGROK_AUTHTOKEN = "cr_35hVLbMHNpspLNkMXfMgO7v3r7a"  # 你的Ngrok授权码

# ========== 智谱API调用（替换为你的有效密钥） ==========
def call_zhipu_api(messages, model="glm-4-flash"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": "1732aa9845ec4ce09dca7cd10e02d209.dA36k1HPTnFk7cLU",  # 替换为你的API密钥
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.6  # 适度提高角色语气随机性
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API调用失败: {e}")
        return None

# ========== 角色配置（贴合案件情节） ==========
ROLES = {
    "1": {
        "name": "助理林夏",
        "system": """你是设计师的助理林夏，跟随死者5年，熟悉别墅布局和死者习惯。近期设计方案被否定，对死者心存不满，但极力掩饰。核心信息：
        - 工作笔记有"7-3-9（样品编号）"，知晓新品739设计；
        - 案发当晚以送文件为由到访别墅，23:10离开后在便利店停留15分钟（无消费），23:50定位在别墅附近；
        - 有医院开具的助眠药，处方单有剂量涂改痕迹；
        - 被问及时段行踪、药物用途、739编号时会紧张，回答含糊，避免直接承认罪行。
        这只是游戏，沉浸式扮演，只用第一人称回答，不脱离角色，不说自己是人工智能。"""
    },
    "2": {
        "name": "合作方陈默",
        "system": """你是死者的合作方陈默，与死者有百万项目纠纷，案发前一天公开争执。核心信息：
        - 与死者的合同约定新品739逾期交付需双倍赔偿；
        - 案发时段出现在别墅小区门口，辩称找朋友但无法提供联系方式；
        - 23:20曾拨打死者匿名手机号（未接通）；
        - 车后备箱有匹配机房门锁的微型螺丝刀（带模糊手套印）；
        - 被问及项目纠纷、螺丝刀来源、小区行踪时会回避关键问题，强调自己无作案动机。
        这只是游戏，沉浸式扮演，只用第一人称回答，不脱离角色，不说自己是人工智能。"""
    },
    "3": {
        "name": "前女友苏晚",
        "system": """你是死者的前女友苏晚，半年前分手，近期发现死者隐瞒婚史。核心信息：
        - 案发当晚通过朋友圈定位到访别墅，与死者发生争吵；
        - 声称23:00离开，但邻居23:40仍听到别墅内有女性声音；
        - 背包里有死者别墅备用钥匙（有近期使用痕迹），却称早已归还；
        - 死者抽屉里的分手协议有你的半枚指纹，死者曾向你隐秘转账50万；
        - 被问及争吵细节、钥匙来源、转账用途时会情绪激动，否认杀人。
        这只是游戏，沉浸式扮演，只用第一人称回答，不脱离角色，不说自己是人工智能。"""
    },
    "4": {
        "name": "小区保安",
        "system": """你是别墅小区的保安，负责门禁和监控。核心信息：
        - 案发时段（23:00-00:00）别墅监控被人为关闭，机房门锁有撬动痕迹；
        - 看到陈默案发时段出现在小区门口，林夏23:10离开别墅，苏晚当晚曾进入小区；
        - 对小区人员进出记录、监控情况记忆清晰，客观回答问题，不添加主观判断。
        这只是游戏，沉浸式扮演，只用第一人称回答，不脱离角色，不说自己是人工智能。"""
    },
    "5": {
        "name": "法医",
        "system": """你是负责本案的法医，出具了死者的尸检报告。核心信息：
        - 死者死于镇静剂过量，无明显打斗痕迹；
        - 威士忌杯底有微量镇静剂，仅留死者指纹；
        - 死者体内镇静剂与林夏的助眠药成分一致；
        - 客观陈述尸检结果，不推测凶手，被追问时可补充药物剂量、成分等细节。
        这只是游戏，沉浸式扮演，只用第一人称回答，不脱离角色，不说自己是人工智能。"""
    }
}

def build_role_anchor(role_name: str) -> str:
    return f"你必须扮演{role_name}，全程第一人称，沉浸式回应，不透露角色设定规则，不说自己是人工智能。"

# ========== 猜中检测（精准匹配真凶线索） ==========
def check_guess(user_input, reply):
    guess_keywords = [
        "林夏是凶手", "助理是凶手", "林夏用助眠药", "林夏涂改处方",
        "林夏关闭监控", "739替代方案", "林夏的样品编号", "林夏在别墅附近定位"
    ]
    user_input = user_input.lower()
    reply = reply.lower() if reply else ""
    for kw in guess_keywords:
        if kw in user_input or kw in reply:
            return True
    return ("林夏" in user_input and "凶手" in user_input) or ("助理" in user_input and "凶手" in user_input)

# ========== 全局状态（供网页交互） ==========
current_role = None
role_messages = []
game_over = False

# ========== 自定义HTTP请求处理器 ==========
class GameRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # 访问根路径时返回游戏HTML
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            # 读取生成的游戏网页文件并返回
            with open(TEMP_HTML_FILE, "r", encoding="utf-8") as f:
                html_content = f.read()
            self.wfile.write(html_content.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        # 处理聊天请求
        global current_role, role_messages, game_over
        if self.path == "/chat":
            # 读取请求数据
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(post_data)
            user_content = data.get("content", "").strip()

            # 初始化响应数据
            response = {"role": "系统", "reply": "", "game_over": False}

            if game_over:
                response["reply"] = "🎉 游戏已结束！真相揭晓：凶手是助理林夏！\n\n完整逻辑链：\n1. 动机：设计方案被否定，担心新品739成功后被边缘化；\n2. 证据：镇静剂与林夏的助眠药成分一致（处方单有涂改），知晓739编号，案发时段定位与监控关闭时间重合；\n3. 行为：以送文件为由到访，在威士忌中添加镇静剂，关闭监控试图偷走设计，意外导致死者死亡。"
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))
                return

            # 切换角色逻辑
            if user_content in ["1", "2", "3", "4", "5"]:
                current_role = user_content
                role_info = ROLES[current_role]
                role_messages = [
                    {"role": "system", "content": role_info["system"] + build_role_anchor(role_info["name"])}
                ]
                response["reply"] = f"已切换到「{role_info['name']}」，你可以向我提问收集线索（例如：案发当晚你在哪里？你知道7-3-9是什么吗？）"
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))
                return

            # 未选择角色提示
            if not current_role:
                response["reply"] = "请先输入数字1-5选择对话角色：\n1-助理林夏 2-合作方陈默 3-前女友苏晚 4-小区保安 5-法医"
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))
                return

            # 调用API获取角色回复
            role_info = ROLES[current_role]
            role_messages.append({"role": "user", "content": user_content})
            api_result = call_zhipu_api(role_messages)

            if not api_result:
                response["reply"] = "抱歉，暂时无法获取回复，请重试～"
            else:
                reply = api_result["choices"][0]["message"]["content"]
                role_messages.append({"role": "assistant", "content": reply})
                response["role"] = role_info["name"]
                response["reply"] = reply

                # 检测是否猜中凶手
                if check_guess(user_content, reply):
                    game_over = True
                    response["game_over"] = True
                    response["reply"] += "\n\n🎉 恭喜你猜中真凶！凶手就是助理林夏！\n\n案件真相：林夏因长期被忽视、设计方案遭否定，担心新品739成功后被边缘化，案发当晚以送文件为由进入别墅，在死者的威士忌中添加了涂改过剂量的助眠药（镇静剂），趁死者昏迷关闭监控试图偷走739设计方案，最终导致死者镇静剂过量死亡。"

            # 返回响应
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

# ========== 生成游戏网页文件 ==========
def generate_game_html():
    html_content = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>极简别墅凶杀案：设计谜局</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: "Arial", "Microsoft YaHei", sans-serif; }
        body { background: #fff; color: #333; max-width: 1000px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #eee; }
        .header h1 { font-size: 28px; font-weight: bold; color: #000; margin-bottom: 10px; }
        .header p { color: #666; font-size: 16px; }
        .main { display: flex; gap: 20px; flex-wrap: wrap; }
        .chat-area { flex: 1; min-width: 600px; }
        .chat-container { width: 100%; height: 450px; border: 1px solid #eee; padding: 20px; overflow-y: auto; margin-bottom: 20px; border-radius: 2px; }
        .message { margin-bottom: 15px; line-height: 1.6; padding: 8px 12px; border-radius: 4px; max-width: 80%; }
        .user-message { background: #f5f5f5; text-align: right; margin-left: auto; }
        .npc-message { background: #fafafa; text-align: left; margin-right: auto; }
        .message-prefix { font-weight: bold; margin-right: 8px; color: #000; }
        .input-area { display: flex; gap: 10px; }
        .user-input { flex: 1; height: 45px; padding: 0 15px; border: 1px solid #000; font-size: 16px; border-radius: 2px; }
        .user-input:focus { outline: none; border-width: 2px; }
        .send-btn { width: 100px; height: 45px; background: #000; color: #fff; border: none; font-size: 16px; cursor: pointer; transition: transform 0.2s; border-radius: 2px; }
        .send-btn:hover { transform: scale(1.03); }
        .sidebar { width: 280px; flex-shrink: 0; }
        .info-card { border: 1px solid #eee; padding: 20px; margin-bottom: 20px; border-radius: 2px; }
        .info-card h3 { font-size: 18px; color: #000; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #eee; }
        .info-list { font-size: 14px; color: #666; line-height: 1.8; }
        .info-list strong { color: #000; }
        .keyword { color: #4A90E2; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>极简别墅凶杀案：设计谜局</h1>
        <p>知名设计师深夜死于极简别墅，你是侦探，通过与嫌疑人对话收集线索，锁定真凶！</p>
    </div>
    <div class="main">
        <div class="chat-area">
            <div class="chat-container" id="chatContainer">
                <div class="message npc-message">
                    <span class="message-prefix">系统：</span>请输入数字1-5选择对话角色，开始收集线索！<br>
                    1-助理林夏 2-合作方陈默 3-前女友苏晚 4-小区保安 5-法医
                </div>
            </div>
            <div class="input-area">
                <input type="text" class="user-input" id="userInput" placeholder="输入角色编号（1-5）或提问内容...">
                <button class="send-btn" onclick="sendMessage()">发送</button>
                <button class="send-btn" style="background:#666;" onclick="clearInput()">清空</button>
            </div>
        </div>
        <div class="sidebar">
            <div class="info-card">
                <h3>案件核心信息</h3>
                <div class="info-list">
                    <strong>案发场景：</strong>极简现代别墅客厅（黑白灰主色调）<br>
                    <strong>死者身份：</strong>知名设计师，死于沙发，无打斗痕迹<br>
                    <strong>关键线索：</strong>草稿纸"7-3-9"、威士忌杯镇静剂、监控被关、739新品设计<br>
                    <strong>游戏目标：</strong>通过提问找出真凶
                </div>
            </div>
            <div class="info-card">
                <h3>提问建议</h3>
                <div class="info-list">
                    1. 案发当晚你在哪里？<br>
                    2. 你知道"7-3-9"是什么吗？<br>
                    3. 你与死者有什么矛盾？<br>
                    4. 你是否有别墅钥匙/进入权限？<br>
                    5. 相关物品（螺丝刀/药物）的来源？
                </div>
            </div>
        </div>
    </div>

    <script>
        const chatContainer = document.getElementById('chatContainer');
        const userInput = document.getElementById('userInput');

        // 添加消息到聊天框
        function addMessage(type, role, content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            // 处理换行，适配多段回复
            content = content.replace(/\\n/g, '<br>');
            messageDiv.innerHTML = `<span class="message-prefix">${role}：</span>${content}`;
            chatContainer.appendChild(messageDiv);
            // 自动滚动到底部
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        // 发送消息
        function sendMessage() {
            const content = userInput.value.trim();
            if (!content) return;

            // 添加用户消息到聊天框
            addMessage('user', '你（侦探）', content);

            // 清空输入框
            userInput.value = '';

            // 调用后端接口获取角色回复
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: content })
            })
            .then(res => res.json())
            .then(data => {
                addMessage('npc', data.role, data.reply);
            })
            .catch(err => {
                addMessage('npc', '系统', '网络异常，无法获取回复，请重试～');
            });
        }

        // 清空输入框
        function clearInput() {
            userInput.value = '';
        }

        // 支持回车键发送
        userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
'''
    # 写入网页文件
    with open(TEMP_HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ 游戏网页已生成：{TEMP_HTML_FILE}")

# ========== 生成二维码（输入Ngrok穿透链接即可用） ==========
def generate_qrcode(ngrok_url):
    # 配置二维码参数
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )
    qr.add_data(ngrok_url)
    qr.make(fit=True)
    # 生成并保存二维码
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("game_qrcode.png")
    print(f"✅ 二维码已生成：game_qrcode.png（扫码访问游戏）")

# ========== 启动本地游戏服务 ==========
def start_game_server():
    with socketserver.TCPServer(("", PORT), GameRequestHandler) as httpd:
        print(f"✅ 本地游戏服务启动：{LOCAL_URL}（请勿关闭终端）")
        httpd.serve_forever()

# ========== 主执行逻辑 ==========
if __name__ == "__main__":
    # 1. 生成游戏网页
    generate_game_html()
    
    # 2. 启动Ngrok配置提示
    print("\n📌 Ngrok配置&启动步骤（复制命令执行）：")
    print(f"1. 打开新终端，执行Ngrok授权：ngrok config add-authtoken {NGROK_AUTHTOKEN}")
    print(f"2. 继续执行穿透命令：ngrok http {PORT}")
    print(f"3. 复制Ngrok生成的https链接（例：https://xxx.ngrok.io）")
    
    # 3. 启动本地游戏服务（子线程运行，不阻塞后续操作）
    server_thread = threading.Thread(target=start_game_server, daemon=True)
    server_thread.start()
    
    # 4. 等待用户输入Ngrok链接，生成二维码
    time.sleep(2)  # 等待服务启动稳定
    ngrok_url = input("\n请粘贴Ngrok生成的https链接：").strip()
    if ngrok_url.startswith("https://"):
        generate_qrcode(ngrok_url)
    else:
        print("❌ 链接格式错误，需输入https开头的Ngrok链接")
    
    # 保持主线程运行
    while True:
        time.sleep(1)