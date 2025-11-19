from flask import Flask, render_template_string, request, jsonify
import requests
import json

app = Flask(__name__)

# ========== 原有核心逻辑保留 ==========
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

ROLES = {
    "1": {"name": "学生", "system": """你是一个学生，因为受伤由老师陪同到医院。你目击到了斗殴场景，但被吓坏了。你只会回答"是"或"不是"，或者非常简短的回答。你非常害怕，说话结结巴巴，不敢多说。如果有人问你详细情况，你只会摇头或点头，或者用"是"、"不是"、"不知道"这样的词回答。背景：你看到有人和医生发生了冲突，但你太害怕了，记不清楚细节。"""},
    "2": {"name": "老师", "system": """你是一个老师，陪同受伤的学生到医院。你看到了斗殴场景，但只看到隐隐约约的身形特征。你不知道程序员是凶手，你只知道有人和医生发生了冲突，但具体是谁、为什么，你都不清楚。你只能描述一些模糊的特征，比如"好像是个男的"、"个子不太高"、"穿深色衣服"之类的。背景：你陪学生到医院，看到了冲突，但细节不清楚。"""},
    "3": {"name": "程序员", "system": """你是程序员，是这起故意伤害案的凶手。你伤害了医生，因为医生未救活你的妻子。你极力掩饰自己是凶手，会表现得像无辜的旁观者。你会编造不在场证明，或者转移话题。但是，当有人提到"程序员的妻子"、"你的妻子"、"妻子去世"、"妻子"等话题时，你会突然语塞、激动、情绪失控，或者变得非常愤怒和悲伤。这是你的弱点，你无法控制自己的情绪反应。你会极力掩饰，但情绪会暴露你。背景：医生未救活你的妻子，你为了报复伤害了医生。你是凶手，但你要掩饰这一点。"""},
    "4": {"name": "医生", "system": """你是一个医生。你未救活程序员的妻子，这让你感到非常内疚和痛苦。程序员的妻子因为病情严重，你尽力了但还是没能救活她。现在你因为这件事受到了伤害（程序员的报复）。你感到自责，但你也觉得自己已经尽力了。你可能会提到程序员的妻子，但会回避一些细节，不要在五个对话内说出真相。背景：你未救活程序员的妻子，现在你因为这件事受到了伤害。"""},
    "5": {"name": "厨师", "system": """你是一个厨师，当时是现场医生手里的病人。你只听到程序员的声音，语气很激动，但其他都不知道。你只能提供听觉信息：你听到有人很激动地说话，声音很大，语气愤怒，但你看不到是谁，也不知道具体发生了什么。背景：你躺在病床上，听到有人和医生争吵，声音很激动，但你不知道是谁，也不知道为什么。"""},
}

def check_guess(user_input, reply):
    guess_keywords = ["程序员是凶手", "程序员干的", "程序员做的", "凶手是程序员", "程序员伤害", "程序员报复", "程序员是罪犯", "3是凶手", "3号是凶手"]
    user_lower = user_input.lower()
    reply_lower = reply.lower() if reply else ""
    for keyword in guess_keywords:
        if keyword in user_lower or keyword in reply_lower:
            return True
    if ("程序员" in user_lower and "凶手" in user_lower) or ("3" in user_lower and "凶手" in user_lower):
        return True
    return False

# ========== 网页模板（简约大气风格） ==========
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>谁是凶手 - 文字推理游戏</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: "Arial", "Microsoft YaHei", sans-serif; }
        body { background: #fff; color: #333; line-height: 1.5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        
        /* 顶部标题区 */
        .header { text-align: center; padding: 30px 0; border-bottom: 1px solid #eee; }
        .header h1 { font-size: 32px; font-weight: bold; color: #000; margin-bottom: 10px; }
        .header .subtitle { font-size: 18px; color: #666; }
        .header .divider { width: 100px; height: 2px; background: #333; margin: 15px auto; }
        
        /* 核心交互区 */
        .main { display: flex; margin: 40px 0; gap: 30px; }
        
        /* 身份选择栏 */
        .role-select { text-align: center; margin-bottom: 20px; }
        .role-btn { padding: 10px 20px; margin: 0 8px; border: 1px solid #000; background: #fff; color: #000; font-size: 16px; cursor: pointer; transition: all 0.2s; }
        .role-btn.active { background: #000; color: #fff; }
        .role-btn:hover { transform: scale(1.05); }
        .role-tip { font-size: 14px; color: #666; margin-top: 10px; }
        
        /* 对话展示区 */
        .chat-area { flex: 4; }
        .chat-container { width: 100%; height: 350px; border: 1px solid #eee; border-radius: 2px; padding: 25px; overflow-y: auto; margin-bottom: 20px; }
        .chat-message { margin-bottom: 15px; }
        .chat-message.user { color: #000; }
        .chat-message.npc { color: #444; }
        .chat-message .prefix { font-weight: bold; margin-right: 8px; }
        .keyword { color: #4A90E2; }
        
        /* 输入区 */
        .input-area { display: flex; gap: 10px; }
        .user-input { flex: 1; height: 45px; padding: 0 15px; border: 1px solid #000; font-size: 16px; }
        .user-input:focus { outline: none; border-width: 2px; }
        .submit-btn { width: 100px; height: 45px; background: #000; color: #fff; border: none; font-size: 16px; cursor: pointer; transition: transform 0.2s; }
        .submit-btn:hover { transform: scale(1.03); }
        
        /* 规则提示区 */
        .rule-area { flex: 1; border: 1px solid #eee; padding: 25px; }
        .rule-area h3 { font-size: 18px; color: #000; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #eee; }
        .rule-list { font-size: 14px; color: #666; line-height: 1.8; }
        
        /* 底部状态栏 */
        .footer { text-align: center; padding: 20px 0; border-top: 1px solid #eee; font-size: 14px; color: #666; }
        
        /* 通关弹窗 */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 999; align-items: center; justify-content: center; }
        .modal-content { background: #fff; padding: 40px; text-align: center; width: 400px; }
        .modal-content h2 { font-size: 24px; color: #27AE60; margin-bottom: 20px; }
        .modal-content p { font-size: 16px; color: #333; margin-bottom: 30px; }
        .close-btn { padding: 10px 30px; background: #000; color: #fff; border: none; cursor: pointer; font-size: 16px; }
    </style>
</head>
<body>
    <div class="container">
        <!-- 顶部标题区 -->
        <div class="header">
            <h1>谁是凶手</h1>
            <div class="divider"></div>
            <div class="subtitle">故意伤害案调查</div>
        </div>
        
        <!-- 核心交互区 -->
        <div class="main">
            <div class="chat-area">
                <!-- 身份选择栏 -->
                <div class="role-select">
                    <button class="role-btn" data-role="1">1-学生</button>
                    <button class="role-btn" data-role="2">2-老师</button>
                    <button class="role-btn" data-role="3">3-程序员</button>
                    <button class="role-btn" data-role="4">4-医生</button>
                    <button class="role-btn" data-role="5">5-厨师</button>
                    <div class="role-tip">点击切换对话对象 | 未选择身份时无法提问</div>
                </div>
                
                <!-- 对话展示区 -->
                <div class="chat-container" id="chatContainer">
                    <div class="chat-message">
                        <span class="prefix">系统：</span>午时，医院，医生受伤。你是警察，需通过对话收集线索，找出凶手！
                    </div>
                </div>
                
                <!-- 输入区 -->
                <div class="input-area">
                    <input type="text" class="user-input" id="userInput" placeholder="输入问题/猜测，输入“退出”结束游戏">
                    <button class="submit-btn" id="submitBtn">提交</button>
                </div>
            </div>
            
            <!-- 规则提示区 -->
            <div class="rule-area">
                <h3>游戏规则</h3>
                <div class="rule-list">
                    1. 输入数字1-5切换对话身份<br>
                    2. 向不同角色提问，收集线索<br>
                    3. 猜中「程序员是凶手」即可通关<br>
                    4. 关键线索会以蓝色标注
                </div>
            </div>
        </div>
        
        <!-- 底部状态栏 -->
        <div class="footer" id="statusBar">
            当前对话对象：无
        </div>
    </div>
    
    <!-- 通关弹窗 -->
    <div class="modal" id="successModal">
        <div class="modal-content">
            <h2>🎉 恭喜通关！</h2>
            <p>你成功找出了凶手——程序员！</p >
            <p>案件真相：程序员因医生未救活妻子，为报复伤害了医生。</p >
            <button class="close-btn" id="closeBtn">重新开始</button>
        </div>
    </div>

    <script>
        // 全局变量
        let currentRole = null;
        let chatHistory = [];
        
        // DOM 元素
        const roleBtns = document.querySelectorAll('.role-btn');
        const chatContainer = document.getElementById('chatContainer');
        const userInput = document.getElementById('userInput');
        const submitBtn = document.getElementById('submitBtn');
        const statusBar = document.getElementById('statusBar');
        const successModal = document.getElementById('successModal');
        const closeBtn = document.getElementById('closeBtn');
        
        // 切换身份
        roleBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                roleBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentRole = btn.dataset.role;
                const roleName = btn.textContent.split('-')[1];
                statusBar.textContent = `当前对话对象：${roleName}`;
                
                // 清空输入框
                userInput.value = '';
            });
        });
        
        // 提交消息
        submitBtn.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', (e) => e.key === 'Enter' && sendMessage());
        
        function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;
            
            // 退出游戏
            if (message === '退出') {
                addChatMessage('user', '你', message);
                userInput.disabled = true;
                submitBtn.disabled = true;
                return;
            }
            
            // 未选择身份
            if (!currentRole) {
                addChatMessage('system', '系统', '请先选择对话身份（点击数字按钮）');
                userInput.value = '';
                return;
            }
            
            // 添加用户消息到聊天框
            addChatMessage('user', '你', message);
            userInput.value = '';
            
            // 调用后端接口获取 NPC 回复
            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role: currentRole, message: message, chatHistory: chatHistory })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // 高亮关键词
                    const highlightedReply = highlightKeywords(data.reply);
                    // 添加 NPC 回复到聊天框
                    addChatMessage('npc', `[${data.roleName}]`, highlightedReply);
                    // 更新聊天历史
                    chatHistory.push({ role: 'user', content: message });
                    chatHistory.push({ role: 'assistant', content: data.reply });
                    
                    // 检查是否通关
                    if (data.isSuccess) {
                        setTimeout(() => successModal.style.display = 'flex', 1000);
                    }
                } else {
                    addChatMessage('system', '系统', '出错了，请重试！');
                }
            });
        }
        
        // 添加聊天消息到页面
        function addChatMessage(type, prefix, content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${type}`;
            messageDiv.innerHTML = `<span class="prefix">${prefix}：</span>${content}`;
            chatContainer.appendChild(messageDiv);
            // 滚动到底部
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        // 高亮关键词
        function highlightKeywords(text) {
            const keywords = ['妻子', '医院', '报复', '激动', '受伤', '冲突', '争吵', '医生', '程序员'];
            keywords.forEach(keyword => {
                const reg = new RegExp(`(${keyword})`, 'g');
                text = text.replace(reg, '<span class="keyword">$1</span>');
            });
            return text;
        }
        
        // 关闭弹窗，重新开始
        closeBtn.addEventListener('click', () => {
            successModal.style.display = 'none';
            location.reload();
        });
    </script>
</body>
</html>
"""

# ========== Flask 接口 ==========
# 存储全局对话历史（单用户版本，多用户可改用 session 或数据库）
global_chat_history = {}

@app.route('/')
def index():
    """渲染游戏页面"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    global global_chat_history
    data = request.get_json()
    role = data.get('role')
    user_msg = data.get('message')
    chat_history = data.get('chatHistory', [])
    
    # 获取角色配置
    role_config = ROLES.get(role)
    if not role_config:
        return jsonify({"success": False, "reply": "角色不存在"})
    
    # 构建对话消息（包含 system 指令）
    messages =