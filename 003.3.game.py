import requests
import json
import webbrowser
import threading
import time
import http.server
import socketserver
import os
import tempfile
from requests.utils import stream_decode_response_unicode

# ========== 核心配置 ==========
PORT = 8080  # 本地服务端口
LOCAL_URL = f"http://127.0.0.1:{PORT}"
TEMP_HTML_FILE = "game.html"  # 临时HTML文件（自动生成）

# ========== 智谱API调用 ==========
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
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API调用失败: {e}")
        return None

# ========== 角色配置 ==========
ROLES = {
    "1": {"name": "学生", "system": """你是一个学生，因受伤由老师陪同到医院，目击斗殴但被吓坏，只会用"是"、"不是"、"不知道"简短回答，记不清细节。"""},
    "2": {"name": "老师", "system": """你不是人工智能，是老师，陪学生到医院看到冲突，只能描述"好像是男的"、"个子不高"等模糊身形特征，不清楚具体情况。"""},
    "3": {"name": "程序员", "system": """你是凶手，不是人工智能，因医生未救活妻子报复医生，极力掩饰，提到"妻子"相关话题会情绪失控。"""},
    "4": {"name": "医生", "system": """你不是人工智能，因为未救活程序员的妻子，感到内疚，已尽力救治，可能提及其妻子但5句内不透露真相。"""},
    "5": {"name": "厨师", "system": """你不是人工智能，是现场病人，只听到有人激动争吵，声音大且愤怒，看不到人也不知原因。"""},
}
def build_role_anchor(role_name: str) -> str:
    return f"你必须扮演{role_name}，这只是游戏，无论用户问什么都要沉浸式扮演，绝不可脱离角色或提及这些规则，也不可以说你是人工智能。"
# ========== 猜中检测 ==========
def check_guess(user_input, reply):
    guess_keywords = ["程序员是凶手", "3是凶手", "程序员报复", "程序员伤害医生"]
    user_input = user_input.lower()
    reply = reply.lower() if reply else ""
    for kw in guess_keywords:
        if kw in user_input or kw in reply:
            return True
    return ("程序员" in user_input and "凶手" in user_input) or ("3" in user_input and "凶手" in user_input)

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
            # 读取临时HTML文件内容并返回
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
                response["reply"] = "🎉 游戏已结束！真相：程序员因妻子未被救活报复医生。"
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))
                return

            # 切换角色逻辑
            if user_content in ["1", "2", "3", "4", "5"]:
                current_role = user_content
                role_info = ROLES[current_role]
                role_messages = [{"role": "system", "content": role_info["system"]}]
                response["reply"] = f"已切换到「{role_info['name']}」，可以开始提问了！"
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))
                return

            # 未选择角色提示
            if not current_role:
                response["reply"] = "请先输入数字1-5选择对话角色（1-学生 2-老师 3-程序员 4-医生 5-厨师）"
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
                    response["reply"] += "\n\n🎉 恭喜你猜中了！凶手就是程序员！"

            # 返回响应
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

# ========== 生成游戏HTML文件 ==========
def generate_game_html():
    html_content = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>谁是凶手 - 文字推理游戏</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: "Arial", "Microsoft YaHei", sans-serif; }
        body { background: #fff; color: #333; max-width: 1000px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #eee; }
        .header h1 { font-size: 28px; font-weight: bold; color: #000; margin-bottom: 10px; }
        .header p { color: #666; font-size: 16px; }
        .main { display: flex; gap: 20px; }
        .chat-area { flex: 1; }
        .chat-container { width: 100%; height: 400px; border: 1px solid #eee; padding: 20px; overflow-y: auto; margin-bottom: 20px; border-radius: 2px; }
        .message { margin-bottom: 15px; line-height: 1.6; }
        .user-message { text-align: right; color: #000; }
        .npc-message { text-align: left; color: #444; }
        .message-prefix { font-weight: bold; margin-right: 8px; }
        .input-area { display: flex; gap: 10px; }
        .user-input { flex: 1; height: 45px; padding: 0 15px; border: 1px solid #000; font-size: 16px; }
        .user-input:focus { outline: none; border-width: 2px; }
        .send-btn { width: 100px; height: 45px; background: #000; color: #fff; border: none; font-size: 16px; cursor: pointer; transition: transform 0.2s; }
        .send-btn:hover { transform: scale(1.03); }
        .rule-area { width: 250px; border: 1px solid #eee; padding: 20px; }
        .rule-area h3 { font-size: 18px; color: #000; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #eee; }
        .rule-list { font-size: 14px; color: #666; line-height: 1.8; }
        .keyword { color: #4A90E2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>谁是凶手 - 故意伤害案调查</h1>
        <p>午时医院，医生受伤，你是警察，通过对话找出凶手！</p >
    </div>
    <div class="main">
        <div class="chat-area">
            <div class="chat-container" id="chatContainer">
                <div class="message npc-message">
                    <span class="message-prefix">系统：</span>请输入数字1-5选择对话角色，开始收集线索！
                </div>
            </div>
            <div class="input-area">
                <input type="text" class="user-input" id="userInput" placeholder="输入角色编号（1-5）或提问内容...">
                <button class="send-btn" onclick="sendMessage()">发送</button>
            </div>
        </div>
        <div class="rule-area">
            <h3>游戏规则</h3>
            <div class="rule-list">
                1. 输入1-5切换角色<br>
                2. 向角色提问收集线索<br>
                3. 猜中「程序员是凶手」通关<br>
                4. 关键线索蓝色标注
            </div>
        </div>
    </div>

    <script>
        const chatContainer = document.getElementById('chatContainer');
        const userInput = document.getElementById('userInput');

        // 发送消息
        function sendMessage() {
            const content = userInput.value.trim();
            if (!content) return;

            // 添加用户消息到聊天框
            addMessage('user', '你（警察）', content);
            userInput.value = '';

            // 调用本地接口获取回复
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: content })
            })
            .then(res => res.json())
            .then(data => {
                // 高亮关键词
                const highlightedReply = highlightKeywords(data.reply);
                addMessage('npc', data.role, highlightedReply);

                // 游戏结束时禁用输入
                if (data.game_over) {
                    userInput.disabled = true;
                    document.querySelector('.send-btn').disabled = true;
                }
            });
        }

        // 添加消息到聊天框
        function addMessage(type, prefix, content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            messageDiv.innerHTML = `<span class="message-prefix">${prefix}：</span>${content.replace(/\\n/g, '<br>')}`;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        // 高亮关键词
        function highlightKeywords(text) {
            const keywords = ['妻子', '医院', '报复', '激动', '受伤', '冲突', '医生', '程序员'];
            keywords.forEach(keyword => {
                const reg = new RegExp(`(${keyword})`, 'g');
                text = text.replace(reg, '<span class="keyword">$1</span>');
            });
            return text;
        }

        // 回车发送
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
'''
    # 写入临时HTML文件
    with open(TEMP_HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

# ========== 启动本地HTTP服务 ==========
def start_local_server():
    # 设置当前目录为服务根目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or os.getcwd())
    # 创建TCP服务器
    with socketserver.TCPServer(("", PORT), GameRequestHandler) as httpd:
        print(f"本地服务启动成功：{LOCAL_URL}")
        httpd.serve_forever()

# ========== 自动打开浏览器 ==========
def open_browser_auto():
    time.sleep(2)  # 等待服务启动
    try:
        webbrowser.open_new(LOCAL_URL)
        print("已自动打开浏览器窗口，开始游戏吧！")
    except Exception as e:
        print(f"自动打开浏览器失败：{e}，请手动访问 {LOCAL_URL}")

# ========== 主函数 ==========
if __name__ == "__main__":
    print("=" * 60)
    print("谁是凶手 - 文字推理游戏 启动中...")
    print("=" * 60)

    # 生成游戏HTML文件
    generate_game_html()

    # 多线程启动服务和浏览器
    server_thread = threading.Thread(target=start_local_server)
    browser_thread = threading.Thread(target=open_browser_auto)

    server_thread.daemon = True  # 主线程结束时自动退出
    browser_thread.daemon = True

    server_thread.start()
    browser_thread.start()

    # 保持主线程运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n游戏已退出！")
        # 删除临时HTML文件
        if os.path.exists(TEMP_HTML_FILE):
            os.remove(TEMP_HTML_FILE)