import streamlit as st
from config import GENDER_OPTIONS, REGION_RATIO, HEIGHT_RANGE, WEIGHT_RANGE, QUESTIONNAIRE_STEPS
from match_algorithm import calculate_match_probability, generate_partner_id
from api_handler import generate_partner_profile, generate_chat_response
from data_manager import save_data, save_chat_record

def render_questionnaire():
    """渲染推进式调查问卷，处理session_state避免KeyError"""
    st.title("🎯 随机伴侣匹配 - 前置问卷")
    # 初始化session_state
    if "questionnaire_step" not in st.session_state:
        st.session_state.questionnaire_step = 0
    if "user_info" not in st.session_state:
        st.session_state.user_info = {"gender": GENDER_OPTIONS[0], "height": 170, "weight": 60, "age": 25}
    if "user_preferences" not in st.session_state:
        st.session_state.user_preferences = {"region": "亚洲", "partner_age": 25, "hobby": "无"}
    if "questionnaire_completed" not in st.session_state:
        st.session_state.questionnaire_completed = False

    step = st.session_state.questionnaire_step
    st.progress((step + 1) / len(QUESTIONNAIRE_STEPS))
    st.subheader(f"步骤 {step + 1}/{len(QUESTIONNAIRE_STEPS)}：{QUESTIONNAIRE_STEPS[step]}")

    # 步骤1：个人信息
    if step == 0:
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("性别", GENDER_OPTIONS, index=GENDER_OPTIONS.index(st.session_state.user_info["gender"]))
            age = st.number_input("年龄", min_value=18, max_value=100, value=st.session_state.user_info["age"])
        with col2:
            height = st.slider("身高(cm)", *HEIGHT_RANGE, value=st.session_state.user_info["height"])
            weight = st.slider("体重(kg)", *WEIGHT_RANGE, value=st.session_state.user_info["weight"])
        # 更新session_state
        st.session_state.user_info.update({"gender": gender, "age": age, "height": height, "weight": weight})

    # 步骤2：偏好设置
    elif step == 1:
        region = st.selectbox("期望伴侣地区", list(REGION_RATIO.keys()), index=list(REGION_RATIO.keys()).index(st.session_state.user_preferences["region"]))
        partner_age = st.number_input("期望伴侣年龄", min_value=18, max_value=100, value=st.session_state.user_preferences["partner_age"])
        hobby = st.text_input("期望伴侣的爱好（选填）", value=st.session_state.user_preferences["hobby"])
        st.session_state.user_preferences.update({"region": region, "partner_age": partner_age, "hobby": hobby})

    # 步骤3：匹配条件确认
    elif step == 2:
        st.write("### 你的信息与偏好")
        st.json(st.session_state.user_info)
        st.json(st.session_state.user_preferences)
        if st.button("确认并开始匹配"):
            st.session_state.questionnaire_completed = True
            save_data({"user_info": st.session_state.user_info, "user_preferences": st.session_state.user_preferences})

    # 步骤导航
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("上一步") and step > 0:
            st.session_state.questionnaire_step -= 1
            st.rerun()
    with col_next:
        if st.button("下一步") and step < len(QUESTIONNAIRE_STEPS) - 1:
            st.session_state.questionnaire_step += 1
            st.rerun()

    return st.session_state.user_info, st.session_state.user_preferences, st.session_state.questionnaire_completed

def render_match_result(user_info: dict, user_preferences: dict):
    """渲染匹配结果与概率"""
    st.title("💘 匹配结果")
    prob = calculate_match_probability(user_info, user_preferences)
    st.metric("匹配成功概率", f"{prob}%")
    st.write("### 你的知心伴侣人物设定")
    # 生成伴侣信息
    if "partner_profile" not in st.session_state:
        st.session_state.partner_profile = generate_partner_profile(user_preferences)
        st.session_state.partner_id = generate_partner_id()
    st.write(st.session_state.partner_profile)
    return st.session_state.partner_profile, st.session_state.partner_id

def render_chat_interface(partner_profile: str, partner_id: str):
    """渲染交流界面，记录对话"""
    st.title("💬 与伴侣交流")
    # 初始化对话历史
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    # 显示对话历史
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.write(chat["content"])
    # 用户输入
    user_input = st.chat_input("对伴侣说点什么吧...")
    if user_input:
        # 记录用户消息
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        # 生成伴侣回复
        with st.spinner("伴侣正在思考..."):
            response = generate_chat_response(partner_profile, user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)
        # 保存交流记录
        save_chat_record(
            user_id=f"user_{st.session_state.user_info['age']}",
            partner_id=partner_id,
            chat={"user": user_input, "partner": response, "time": st.runtime.state.get_session_id()}
        )