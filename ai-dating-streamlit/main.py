import streamlit as st
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import QUESTIONS, UNREAL_WEB_SERVER_URL, UNREAL_SCENE_PATH
from app.utils.data_handler import (
    save_player_info, save_partner_info, save_chat_record,
    get_player_info, get_partner_info, get_chat_records
)
from app.utils.match_algorithm import match_best_partner
from app.utils.ai_handler import generate_partner_reply

# Streamlit页面配置
st.set_page_config(
    page_title="AI伴侣匹配与交流",
    page_icon="💖",
    layout="wide"
)

# 全局状态管理（使用session_state存储玩家ID、伴侣信息等）
if "player_id" not in st.session_state:
    st.session_state.player_id = None
if "partner_info" not in st.session_state:
    st.session_state.partner_info = None
if "chat_records" not in st.session_state:
    st.session_state.chat_records = []
if "page" not in st.session_state:
    st.session_state.page = "survey"  # survey/match_result/chat

# ---------------------- 1. 问卷页面 ----------------------
def show_survey():
    st.title("💖 玩家信息调查问卷")
    st.subheader("填写以下信息，为你匹配最契合的伴侣～")

    # 表单收集数据
    with st.form(key="survey_form"):
        player_info = {}
        for q in QUESTIONS:
            st.markdown(f"### {q['id']}. {q['title']}")
            if q["type"] == "radio":
                answer = st.radio(
                    label=q["title"],
                    options=q["options"],
                    key=q["key"],
                    index=None
                )
            elif q["type"] == "number":
                answer = st.number_input(
                    label=q["title"],
                    min_value=q["min"],
                    max_value=q["max"],
                    key=q["key"],
                    step=1
                )
            elif q["type"] == "multiselect":
                answer = st.multiselect(
                    label=q["title"],
                    options=q["options"],
                    key=q["key"]
                )
            player_info[q["key"]] = answer

        # 提交按钮
        submit_btn = st.form_submit_button(label="提交并匹配伴侣", type="primary")
        if submit_btn:
            # 数据验证
            if not all(player_info.values()):
                st.error("❌ 请填写所有必填项！")
                return
            if not (145 <= player_info["height"] <= 220):
                st.error("❌ 身高必须在145-220cm之间！")
                return
            if not player_info["hobbies"]:
                st.error("❌ 兴趣爱好至少选择一项！")
                return

            # 保存玩家信息，获取player_id
            player_id = save_player_info(player_info)
            st.session_state.player_id = player_id

            # 匹配伴侣
            match_result = match_best_partner(player_info)
            st.session_state.partner_info = match_result["best_partner"]
            st.session_state.match_score = match_result["best_score"]
            st.session_state.suggestions = match_result["suggestions"]

            # 保存伴侣信息
            save_partner_info(match_result["best_partner"], player_id)

            # 跳转到匹配结果页面
            st.session_state.page = "match_result"
            st.rerun()

# ---------------------- 2. 匹配结果页面 ----------------------
def show_match_result():
    if not st.session_state.player_id or not st.session_state.partner_info:
        st.session_state.page = "survey"
        st.rerun()

    partner = st.session_state.partner_info
    match_score = st.session_state.match_score
    suggestions = st.session_state.suggestions

    st.title("🎉 匹配成功！")
    st.subheader(f"你的专属伴侣：{partner['name']}")

    # 伴侣信息卡片
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(partner["avatar"], width=150)
        st.metric(label="匹配度", value=f"{match_score}%")
    with col2:
        st.write(f"**性别**：{partner['gender']}")
        st.write(f"**年龄**：{partner['age']}")
        st.write(f"**身高**：{partner['height']}cm")
        st.write(f"**体重**：{partner['weight']}kg")
        st.write(f"**性格**：{partner['personality']}")
        st.write(f"**爱好**：{','.join(partner['hobbies'])}")
        st.write(f"**背景**：{partner['background']}")

    # 匹配建议
    st.markdown("### 💡 匹配建议")
    for suggestion in suggestions:
        st.write(f"- {suggestion}")

    # 操作按钮
    col3, col4 = st.columns(2)
    with col3:
        if st.button("开始聊天 🗣️", type="primary"):
            # 加载聊天记录
            st.session_state.chat_records = get_chat_records(st.session_state.player_id)
            st.session_state.page = "chat"
            st.rerun()
    with col4:
        unreal_url = f"{UNREAL_WEB_SERVER_URL}{UNREAL_SCENE_PATH}?player_id={st.session_state.player_id}"
        st.markdown(f"[跳转至虚幻引擎场景 🎮]({unreal_url})", unsafe_allow_html=True)

# ---------------------- 3. 聊天页面 ----------------------
def show_chat():
    if not st.session_state.player_id or not st.session_state.partner_info:
        st.session_state.page = "survey"
        st.rerun()

    player_id = st.session_state.player_id
    partner = st.session_state.partner_info
    chat_records = st.session_state.chat_records

    st.title(f"🗣️ 与{partner['name']}聊天")

    # 聊天历史
    chat_container = st.container(height=400)
    with chat_container:
        for record in chat_records:
            # 玩家消息
            st.chat_message("user").write(f"你：{record['player_msg']}")
            # 伴侣消息
            st.chat_message("assistant", avatar=partner["avatar"]).write(f"{partner['name']}：{record['partner_msg']}")
        if not chat_records:
            st.write(f"💬 开始与{partner['name']}聊天吧！")

    # 消息输入框
    player_info = get_player_info(player_id)
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([8, 1])
        with col1:
            player_msg = st.text_input(label="输入消息", placeholder="想说点什么...")
        with col2:
            send_btn = st.form_submit_button(label="发送")

        if send_btn and player_msg.strip():
            try:
                # 生成AI回复
                partner_reply = generate_partner_reply(player_msg.strip(), player_info, partner)
                # 保存聊天记录
                new_record = save_chat_record(player_id, player_msg.strip(), partner_reply, partner["name"])
                # 更新会话中的聊天记录
                st.session_state.chat_records.append(new_record)
                # 刷新页面
                st.rerun()
            except Exception as e:
                st.error(f"❌ 发送失败：{str(e)}")

    # 跳转按钮
    unreal_url = f"{UNREAL_WEB_SERVER_URL}{UNREAL_SCENE_PATH}?player_id={player_id}"
    st.markdown(f"[跳转至虚幻引擎场景 🎮]({unreal_url})", unsafe_allow_html=True)

# ---------------------- 页面路由 ----------------------
if st.session_state.page == "survey":
    show_survey()
elif st.session_state.page == "match_result":
    show_match_result()
elif st.session_state.page == "chat":
    show_chat()