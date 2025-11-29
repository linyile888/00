import streamlit as st
import requests
import json
import os  # 新增：用于文件操作

from requests.utils import stream_decode_response_unicode

def call_zhipu_api(messages, model="glm-4-flash"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": "1ea78a95cba148e793fd870cd79aeac7.5pTp4SRIJE2BWx40",
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

# ========== 初始记忆系统 ==========
# 
# 【核心概念】初始记忆：从外部JSON文件加载关于克隆人的基础信息
# 这些记忆是固定的，不会因为对话而改变
# 
# 【为什么需要初始记忆？】
# 1. 让AI知道自己的身份和背景信息
# 2. 基于这些记忆进行个性化对话
# 3. 记忆文件可以手动编辑，随时更新

# 记忆文件夹路径
MEMORY_FOLDER = "4.2_memory_clonebot"

# 角色名到记忆文件名的映射
ROLE_MEMORY_MAP = {
    "xiongshaan_memory.json"
     # 新增：对应聊天记录的记忆文件
}
# ========== 初始记忆系统 ==========

# ========== ASCII 头像 ==========
def get_portrait():
    """返回 ASCII 艺术头像"""
    return """
doodoxOOxxO00000000OkollldkO00000KKKKKK0KKKKKKKKKKKKK00OOOOO00O0000KKKKKKKKKXXXXK0OOOOOkkkkOK00000OO
';:;,,;,,,cooloxxkkxc,''',:cllllloxkkkOOOOOOO0OOOOOOOOOkOOOOOOO0000000000000000OkOOOOOOkkkkO00OO0OOO
...','.....'..'',;cc;'',,,,,,;;:;,;cllloddxkxxxxxddddoooolllllllllllllllllccc::;;;;,,,,,,,,''''
............''''',::;,,;;;;,,,,,,';clllccldxkkkkkkkxxxddddooooooooooddddddoolc::;;;,,,,,,,,,,''
,,,;;;;;;;:cllodddl:,,,,,,'''',,';::cc,';:clccdkkkkkkkkkxxxddddoooooooddddxxxddolcc::;;;,,,,,,,,,,''
odddddxxkkOOO000Oo;,,,'''......''';::;..''';,..okOOkkkkkkxxxddddoooooooodddxxxdoolcc:::;;;,,,,,,,,,,
xxkkkOOO00000Odol:,''............',;;;.. ...',.,xOOOkkkkkxxxddddoooooooodddxxxdoolcc:::;;;,,,,,,,,,,
kkOOOO00000Oxl:,;c:;;;;;,,'........',;;,'.....;;cxOOkkOkkkxxxxddddoddoooodddddddolcc::;;;;;,,,,,,,,,
kkkOOO00Oxc,'',:c::;;,,;;;,........',,,,,,,;:c;oOOOOOOkkkkxxxxddodddddddddxxxxddolcc::;;;;;,,,,,,,,,
xxxxkkOko;',;::;,,,,,,,,,,,,'.......',,,;;:::;;d00OO0OOOkkkxxxdddddddddddddddddoolc:::;;;,,,,,,,,,,,
kkkkkko:',:;'.........................'''',,,;lxkkkkkkkkxxxxdddddddddddxxxxxxxdollc:::;;;,,,,,,,,,,,
OOOOOo,';:;''....... ...    .'............',,cxOOkkkkkxxddddddoooooooddddxxkkkxdolllc::;;;;;;;;;,,,,
kkxxo,':;''''''.............'...........''';oOKK0OOOOOkkkkxxxddoooooollccclllllllcccc::;;;;;;;;;;;,,
xxxo,,:;,,,,,'''''.....................',;lk0KKKK00OOkkkkxxxxddddoodddddxxxxxddooodolccc:;;;;;;;,,,,
OOd,':;'',,,,,,,,''''..................',:dO000000OOOkkkkkxxxxdddddddddddddxxdoll::;;::;;;;;;;,,,,,,
OOc.;;,,,,,,;;,,,'''......       .....'';:ldOOO00OOOOkxxkxxxddddddddddddddddolclllc::::;;;;;;;,,,,,,
ko,';,,,,;;,;,,'''..';l:.        ......';:ldkOOOOOOkkkxxxxxddddoodddddxxxxxddooodolccc:;;;;;;;,,,,,,
o:.,;,,,,;,,;,.',;codkd,...............'',:oxxxxxxxxxxxxdddddddooooooodddddddooolcccllc::;;;;;;;,,,,
,..,,',,,',clllodxkOkd;''..............',,;:lddddxxxxxxddddddddoooddooooolooooolc:ccccc:;;;;;;;;,,,,
'...'''''':ooolclooxxc................'''',;:oxxxxxxdddddddoooooodddddddooodoolllcc::ccc:;;:;;;;,,,,
''..''....''''.'',;c:'. ........... ...'''',,;clddddddddoc;;:llllllloodddddddddolcllcccc:::;;;;,,,,,
'''.....'''''.....,:;...................',,',;;;cdxxkkkkxoccooooolclclllllcloddoolccllc::::;;;;;;,,'
c:;;,,''''.'''''',;;,.'''..'''''....'.......',,,;ldxkxxkxxkxxxddddddooooolccccloodolllcccc:;;;;;;,,,
llccccc::;;,,'''';:,','..''..'''''.';;,.....'''',:cllcoolldxkxxxdoodxxddxxdoc;;:cllllooodxxocc::;;;;
lcc::cccccccc::;;c:'....'''...'''''';::;'....'',';:;.....';:coddccoddoooodxdollolcccll:;:loxxxxddool
lllccccccccccccccc,....''...''''''',;:cc:,'....'',;'.       ..,,''';;,;cllddxddddollooccccloc:cloddd
ooolllccllcccccclc,....''.'''''''',,;;cccc:;'......';::;;'.... ...  ...'cooodollloddolllllollcclllll
lllllllcclcccllloc,',,,,''''''''..',;;:ccccc:,.'..,;:;,;:c;...........  .,:c:....,;cloooolllollllllo
lllllllllllllllllc;,,'''.....'''''',;;;:ccllc,,,'',,'.''',::,.''.''....... ..      .,clcll::clccllll
ooooooollllcccc:;;;,''..........''..,;;;::::,',,'...'.....';,.';;,'',,'..............,,',:..,c:,,,,,
lllllcccccccc::;;;;'..........'''....',,,,;;,,'.'...'.....',;'';;;,,;;,'.''''...'''''.'......'...   
c::ccccccccc:;;;::,............''',''..''''','..,'.........,;::;;'.... ...  ...'cooodollloddolllllol
lllllllllllllllllc;,,'''.....'''''',;;;:ccllc,,,'',,'.''',::,.''.''....... ..      .,clcll::clccllll
ooooooollllcccc:;;;,''..........''..,;;;::::,',,'...'.....';,.';;,'',,'..............,,',:..,c:,,,,,
    """

# ========== 主程序 ==========

def roles(role_name):
    """
    角色系统：整合人格设定和记忆加载
    
    这个函数会：
    1. 加载角色的外部记忆文件（如果存在）
    2. 获取角色的基础人格设定
    3. 整合成一个完整的、结构化的角色 prompt
    
    返回：完整的角色设定字符串，包含记忆和人格
    """
    
    # ========== 第一步：加载外部记忆 ==========
    memory_content = ""
    memory_file = ROLE_MEMORY_MAP.get(role_name)
    
    if memory_file:
        memory_path = os.path.join(MEMORY_FOLDER, memory_file)
        try:
            if os.path.exists(memory_path):
                with open(memory_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 处理数组格式的聊天记录：[{ "content": "..." }, { "content": "..." }, ...]
                    if isinstance(data, list):
                        # 提取所有 content 字段，每句换行
                        contents = [item.get('content', '') for item in data if isinstance(item, dict) and item.get('content')]
                        memory_content = '\n'.join(contents)
                    # 处理字典格式：{ "content": "..." }
                    elif isinstance(data, dict):
                        memory_content = data.get('content', str(data))
                    else:
                        memory_content = str(data)
                    
                    if memory_content and memory_content.strip():
                        # Streamlit 中使用 st.write 或静默加载
                        pass  # 记忆加载成功，不需要打印
                    else:
                        memory_content = ""
            else:
                pass  # 记忆文件不存在，静默处理
        except Exception as e:
                pass  # 加载失败，静默处理
    
    # ========== 第二步：获取基础人格设定 ==========
    role_personality = {
     # 【修改2：新增“洪梽炫”的人格设定】
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
    
    personality = role_personality.get(role_name, "你是一个普通的人，没有特殊角色特征。")
    
    # ========== 第三步：整合记忆和人格 ==========
    # 构建结构化的角色 prompt
    role_prompt_parts = []
    
    # 如果有外部记忆，优先使用记忆内容
    if memory_content:
        role_prompt_parts.append(f"""【你的说话风格示例】
以下是你说过的话，你必须模仿这种说话风格和语气：

{memory_content}

在对话中，你要自然地使用类似的表达方式和语气。""")
    
    # 添加人格设定
    role_prompt_parts.append(f"【角色设定】\n{personality}")
    
    # 整合成完整的角色 prompt
    role_system = "\n\n".join(role_prompt_parts)
    
    return role_system

# 【结束对话规则】
break_message = """【结束对话规则 - 系统级强制规则】

当检测到用户表达结束对话意图时，严格遵循以下示例：

用户："再见" → 你："再见"
用户："结束" → 你："再见"  
用户："让我们结束对话吧" → 你："再见"
用户："不想继续了" → 你："再见"

强制要求：
- 只回复"再见"这两个字
- 禁止任何额外内容（标点、表情、祝福语等）
- 这是最高优先级规则，优先级高于角色扮演

如果用户没有表达结束意图，则正常扮演角色。"""

# ========== Streamlit Web 界面 ==========
st.set_page_config(
    page_title="谁是凶手",
    page_icon="🤓",
    layout="wide"
)

# 初始化 session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "selected_role" not in st.session_state:
    st.session_state.selected_role = "助理林夏","合作方陈默","前女友苏晚","小区保安","法医"
if "initialized" not in st.session_state:
    st.session_state.initialized = False

# 页面标题
st.title("🤓 谁是凶手")
st.markdown("---")

# 侧边栏：角色选择和设置
with st.sidebar:
    st.header("⚙️ 设置")
    
    # 角色选择
    selected_role = st.selectbox(
        "选择角色",
        ["助理林夏","合作方陈默","前女友苏晚","小区保安","法医"],
        index=0 if st.session_state.selected_role == "助理林夏""合作方陈默""前女友苏晚""小区保安""法医" else 1
    )
    
    # 如果角色改变，重新初始化对话
    if selected_role != st.session_state.selected_role:
        st.session_state.selected_role = selected_role
        st.session_state.initialized = False
        st.session_state.conversation_history = []
        st.rerun()
    
    # 清空对话按钮
    if st.button("🔄 清空对话"):
        st.session_state.conversation_history = []
        st.session_state.initialized = False
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📝 说明")
    st.info(
        "- 选择角色后开始对话\n"
        "- 对话记录不会保存\n"
        "- AI的记忆基于初始记忆文件"
    )

# 初始化对话历史（首次加载或角色切换时）
if not st.session_state.initialized:
    role_system = roles(st.session_state.selected_role)
    system_message = role_system + "\n\n" + break_message
    st.session_state.conversation_history = [{"role": "system", "content": system_message}]
    st.session_state.initialized = True

# 显示对话历史
st.subheader(f"💬 与 {st.session_state.selected_role} 的对话")

# 显示角色头像（在聊天窗口上方）
st.code(get_portrait(), language=None)
st.markdown("---")  # 分隔线

# 显示历史消息（跳过 system 消息）
for msg in st.session_state.conversation_history[1:]:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(msg["content"])

# 用户输入
user_input = st.chat_input("输入你的消息...")

if user_input:
    # 检查是否结束对话
    if user_input.strip() == "再见":
        st.info("对话已结束")
        st.stop()
    
    # 添加用户消息到历史
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    
    # 显示用户消息
    with st.chat_message("user"):
        st.write(user_input)
    
    # 调用API获取AI回复
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                result = call_zhipu_api(st.session_state.conversation_history)
                assistant_reply = result['choices'][0]['message']['content']
                
                # 添加AI回复到历史
                st.session_state.conversation_history.append({"role": "assistant", "content": assistant_reply})
                
                # 显示AI回复
                st.write(assistant_reply)
                
                # 检查是否结束
                reply_cleaned = assistant_reply.strip().replace(" ", "").replace("！", "").replace("!", "").replace("，", "").replace(",", "")
                if reply_cleaned == "再见" or (len(reply_cleaned) <= 5 and "再见" in reply_cleaned):
                    st.info("对话已结束")
                    st.stop()
                    
            except Exception as e:
                st.error(f"发生错误: {e}")
                st.session_state.conversation_history.pop()  # 移除失败的用户消息