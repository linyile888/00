import streamlit as st
import requests
import json
import webbrowser
import threading
import time
import http.server
import socketserver
import socket
import importlib
import os
from requests.utils import stream_decode_response_unicode
 
qrcode = None

# ========== 核心配置 ==========
PORT = 8080  # 本地服务端口
LOCAL_URL = f"http://127.0.0.1:{PORT}"
TEMP_HTML_FILE = "design_mystery_game.html"  # 临时HTML文件（自动生成）
QR_IMAGE_FILE = "mystery_game_qr.png"


def get_lan_url() -> str:
    """获取局域网可访问的URL，用于移动设备访问。"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        return f"http://{ip}:{PORT}"
    except Exception:
        return ""


def ensure_qrcode_loaded() -> bool:
    """懒加载 qrcode 库，避免环境未安装时报错。"""
    global qrcode
    if qrcode is not None:
        return True
    try:
        qrcode = importlib.import_module("qrcode")
        return True
    except ModuleNotFoundError:
        return False


def generate_qr_code(url: str):
    """生成指向指定URL的二维码图片。"""
    if not url:
        return
    if not ensure_qrcode_loaded():
        print("未安装 qrcode 库，跳过二维码生成。可执行 'pip install qrcode[pil]' 后重新运行。")
        return
    try:
        img = qrcode.make(url)
        img.save(QR_IMAGE_FILE)
        print(f"二维码已生成：{QR_IMAGE_FILE}，手机扫码即可体验。")
    except Exception as e:
        print(f"二维码生成失败：{e}")
QR_IMAGE_FILE = "mystery_game_qr.png"

# ========== 智谱API调用（请替换为你的有效密钥） ==========
def call_zhipu_api(messages, model="glm-4-flash"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": "1ea78a95cba148e793fd870cd79aeac7.5pTp4SRIJE2BWx40",  # 替换为你的API密钥
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.6  # 适度提高随机性，贴合角色语气
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
def get_portrait():
    """返回 ASCII 艺术头像"""
    return """
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
        elif self.path == f"/{QR_IMAGE_FILE}" and os.path.exists(QR_IMAGE_FILE):
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()
            with open(QR_IMAGE_FILE, "rb") as img_file:
                self.wfile.write(img_file.read())
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
                role_name = current_role if current_role else "未知角色"
                break_message = f"🎉 游戏已结束！本次对话角色为{role_name}，真相揭晓：凶手是助理林夏！\n\n完整逻辑链：\n1. 动机：设计方案被否定，担心新品739成功后被边缘化；\n2. 证据：镇静剂与林夏的助眠药成分一致（处方单有涂改），知晓739编号，案发时段定位与监控关闭时间重合；\n3. 行为：以送文件为由到访，在威士忌中添加镇静剂，关闭监控试图偷走设计，意外导致死者死亡。"
                response["reply"] = break_message
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
        elif self.path == f"/{QR_IMAGE_FILE}" and os.path.exists(QR_IMAGE_FILE):
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()
            with open(QR_IMAGE_FILE, "rb") as img_file:
                self.wfile.write(img_file.read())
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
                role_name = current_role if current_role else "未知角色"
                break_message = f"🎉 游戏已结束！本次对话角色为{role_name}，真相揭晓：凶手是助理林夏！\n\n完整逻辑链：\n1. 动机：设计方案被否定，担心新品739成功后被边缘化；\n2. 证据：镇静剂与林夏的助眠药成分一致（处方单有涂改），知晓739编号，案发时段定位与监控关闭时间重合；\n3. 行为：以送文件为由到访，在威士忌中添加镇静剂，关闭监控试图偷走设计，意外导致死者死亡。"
                response["reply"] = break_message
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

st.set_page_config(
    page_title="AI角色扮演聊天",
    page_icon="🤓",
    layout="wide"
)
with st.sidebar:
    st.header("⚙️ 设置")
    
    # 角色选择
    selected_role = st.selectbox(
        "选择角色",
        ["1","2","3","4","5"],
        index=0 if st.session_state.selected_role == ["1","2","3","4","5"] else 1
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
break_message = "\n\n🎉 恭喜你猜中真凶！凶手就是助理林夏！\n\n案件真相：林夏因长期被忽视、设计方案遭否定，担心新品739成功后被边缘化，案发当晚以送文件为由进入别墅，在死者的威士忌中添加了涂改过剂量的助眠药（镇静剂），趁死者昏迷关闭监控试图偷走739设计方案，最终导致死者镇静剂过量死亡。"
if not st.session_state.initialized:
    role_system =ROLES (st.session_state.selected_role)
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