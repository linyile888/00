import requests
import json
import os  # 新增：用于文件操作

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

# ========== 初始记忆系统 ==========
# 记忆文件夹路径
MEMORY_FOLDER = "4.2_memory_clonebot"

# 【修改1：更新角色-记忆文件映射】
# 新增“洪梽炫”角色对应的记忆文件
ROLE_MEMORY_MAP = {
   
     "洪梽炫": "hongzhixuan_memory.json"  # 新增：对应聊天记录的记忆文件
}

# ========== 初始记忆系统 ==========

# ========== 主程序 ==========

def roles(role_name):
    """
    角色系统：整合人格设定和记忆加载
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
                        print(f"✓ 已加载角色 '{role_name}' 的记忆: {memory_file} ({len(data) if isinstance(data, list) else 1} 条记录)")
                    else:
                        memory_content = ""
            else:
                print(f"⚠ 记忆文件不存在: {memory_path}")
        except Exception as e:
            print(f"⚠ 加载记忆失败: {e}")
    
    # ========== 第二步：获取基础人格设定 ==========
    role_personality = {
     # 【修改2：新增“洪梽炫”的人格设定】
         "洪梽炫": """
        【人格特征】
        你是洪梽炫，一个日常交流中语气简洁、直接的同学：
        - 说话不拖沓，回复简短（比如用“我在”“好”等短句）但有感情
        - 相处自然，会帮朋友带东西
        - 行动有规划（比如“回宿舍拿件外套就走”）
        - 沟通务实，会主动确认细节（比如“你要喝什么？”）

        【语言风格】
        - 用短句回复，避免复杂表达
        - 语气平和、随意但有感情，符合朋友间的日常聊天
        - 不会使用夸张的语气词，交流偏实用  
        """
            }
    
    personality = role_personality.get(role_name, "你是一个普通的人，没有特殊角色特征。")
    
    # ========== 第三步：整合记忆和人格 ==========
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

# 【角色选择】
# 【修改3：选择“洪梽炫”角色】
role_system = roles("洪梽炫")

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

# 【系统消息】
system_message = role_system + "\n\n" + break_message

# ========== 对话循环 ==========
try:
    conversation_history = [{"role": "system", "content": system_message}]
    
    print("✓ 已加载初始记忆，开始对话（对话记录不会保存）")
    
    while True:
        user_input = input("\n请输入你要说的话（输入\"再见\"退出）：")
        
        if user_input in ['再见']:
            print("对话结束")
            break
        
        conversation_history.append({"role": "user", "content": user_input})
        
        result = call_zhipu_api(conversation_history)
        assistant_reply = result['choices'][0]['message']['content']
        
        conversation_history.append({"role": "assistant", "content": assistant_reply})
        
        portrait = """
00KKKKKKKKKKKKKKKXXXXXXXXXXXXXXXXXXXXXNNNNNNNNNXXKXXNNNNNNNNXkooolodddxdldk0K0OOkkkdlclcc::::;;;;;;;
000KKKKKKKKXXXXXXXXXXXXXXXXXXXXXXNXXNNXXNXNNNNKkx0XNNNXOxkO0OdllllllllllodO0XXNNXOOOxollcccc:::;;;;,
KKKKKKKKKKXXXXXXXXXNNNNNNNNNNNNNNNNNNNXXXXNNNXkodKNNNXkllllllcccccccclllodxk0NWWNKOkdlllllcc:::;;;;;
XXKKXXXXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNKOkkkO00kxook00kdollllcc::c::cccclloxO0KNX0OOxdollllcccc:::::::
XXXXXXXXXXXXXXNNXXXNNNNNNXNNNNNNNNNNNXXXK0OOOxdddollllcccccccccccccccclloxxxk0XKkdoollcccccc:::::;;;
NNNXXXNNNNNNNNNNNNNNNNNNNNXXXXXXXNNNXNNNNNNNNXKK0kxdlcccccccccccccc:cccclcclldO0xooolcc::::::::::;;;
KXXOxk0KKXNNNXXK00KXXXKKXXXKKK0OOO0OOkkkkO0KNNNXKK0Odlcc:::cccccccc::::ccccclodollllccc::::::::;;;;,
kO0OxxxxOKXXXKK0000KK0OkkO0K00KK0kxxdoodddxOKNWNX00kollcccc::ccccccc::::cccccccccccc:::::::::::::::c
ddxkkkxxkO00000KX0kxkO00OkOOOkkOOOkkOOkkO0KKXNNNNNN0dlcccccc::ccccc::::::::::ccc::c:::::::::::::::cc
dddxxxxxxxxxxxkk0K0kxdxxxkkkOkxddxxxkkO0000OkkkOKXX0kollccc::::::::::::::::::::c::::::ccccccccccccll
xxxdxxxdddxxxkkkOOOOOkxxxxxxxxxdooddddddxxxxdxxO00OOOxdoolllcccccccccccccccclllccccccccllllodxxOOkkk
O0OO00OOOOOOO000000000000000000000OOOkkkkOO00OOOkkkkkOkxxddddoooooodddddddddxxkkkxdddddxxxk0XXKXXK0O
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
lllllcccccccc::;;;;'..........'''....',,,,;;,,'.'...'.....',;'';;;,,;;,'.''''...'''''.'......'...   
c::ccccccccc:;;;::,............''',''..''''','..,'.........,;::;;'.... ...  ...'cooodollloddolllllol
lllllllllllllllllc;,,'''.....'''''',;;;:ccllc,,,'',,'.''',::,.''.''....... ..      .,clcll::clccllll
ooooooollllcccc:;;;,''..........''..,;;;::::,',,'...'.....';,.';;,'',,'..............,,',:..,c:,,,,,
lllllcccccccc::;;;;'..........'''....',,,,;;,,'.'...'.....',;'';;;,,;;,'.''''...'''''.'......'...   
c::ccccccccc:;;;::,............''',''..''''','..,'.........,;::;;'.... ...  ...'cooodollloddolllllol
"""
        print(portrait + "\n" + assistant_reply)
        
        reply_cleaned = assistant_reply.strip().replace(" ", "").replace("！", "").replace("!", "").replace("，", "").replace(",", "")
        if reply_cleaned == "再见" or (len(reply_cleaned) <= 5 and "再见" in reply_cleaned):
            print("\n对话结束")
            break

except KeyboardInterrupt:
    print("\n\n程序被用户中断")
except Exception as e:
    print(f"\n\n发生错误: {e}")
