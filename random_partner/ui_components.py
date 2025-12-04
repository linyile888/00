import streamlit as st
import plotly.express as px
from config import (
    PARTNER_ERAS, PARTNER_JOBS, REGION_RATIO, ORIENTATION_RATIO,
    QUESTIONNAIRE_STEPS, GENDER_OPTIONS, HEIGHT_RANGE, WEIGHT_RANGE,
    USER_HOBBIES_OPTIONS, PARTNER_PERSONALITY_TYPES
)

# ========== 新增：推进式问卷组件（修复 KeyError） ==========
def render_questionnaire() -> tuple[dict, dict, bool]:
    """
    渲染推进式问卷（分2步）
    :return: (玩家基本信息, 玩家偏好, 是否完成问卷)
    """
    # 安全初始化问卷状态（确保所有键存在）
    if "questionnaire_step" not in st.session_state:
        st.session_state.questionnaire_step = 1
    
    # 初始化玩家基本信息（确保每个键都有默认值）
    if "user_info" not in st.session_state:
        st.session_state.user_info = {
            "gender": GENDER_OPTIONS[0],
            "age": 25,
            "height": 170,
            "weight": 60
        }
    # 补全缺失的键（防止部分键被删除）
    required_user_keys = ["gender", "age", "height", "weight"]
    for key in required_user_keys:
        if key not in st.session_state.user_info:
            st.session_state.user_info[key] = GENDER_OPTIONS[0] if key == "gender" else 25 if key == "age" else 170 if key == "height" else 60
    
    # 初始化玩家偏好（确保每个键都有默认值）
    if "user_preferences" not in st.session_state:
        st.session_state.user_preferences = {
            "region": "全球",
            "orientation": "不限",
            "personality": PARTNER_PERSONALITY_TYPES[0],
            "hobbies": []
        }
    # 补全缺失的键
    required_prefer_keys = ["region", "orientation", "personality", "hobbies"]
    for key in required_prefer_keys:
        if key not in st.session_state.user_preferences:
            st.session_state.user_preferences[key] = "全球" if key == "region" else "不限" if key == "orientation" else PARTNER_PERSONALITY_TYPES[0] if key == "personality" else []
    
    current_step = st.session_state.questionnaire_step
    step_config = QUESTIONNAIRE_STEPS[current_step - 1]
    
    # 问卷标题与进度
    st.markdown(f"""
    ### 📝 {step_config['step']}/{len(QUESTIONNAIRE_STEPS)} {step_config['title']}
    <p style="color: #666; margin-bottom: 20px;">{step_config['desc']}</p>
    """, unsafe_allow_html=True)
    
    # 步骤1：基本信息（修复 gender 索引获取逻辑）
    if current_step == 1:
        col1, col2 = st.columns(2)
        with col1:
            # 安全获取 gender 索引（防止值不在选项中）
            gender_value = st.session_state.user_info["gender"]
            gender_index = GENDER_OPTIONS.index(gender_value) if gender_value in GENDER_OPTIONS else 0
            gender = st.selectbox(
                "你的性别",
                options=GENDER_OPTIONS,
                index=gender_index
            )
            
            age = st.slider(
                "你的年龄",
                min_value=18,
                max_value=60,
                value=st.session_state.user_info["age"],
                step=1
            )
        with col2:
            height = st.slider(
                "你的身高（cm）",
                min_value=HEIGHT_RANGE[0],
                max_value=HEIGHT_RANGE[1],
                value=st.session_state.user_info["height"],
                step=1
            )
            weight = st.slider(
                "你的体重（kg）",
                min_value=WEIGHT_RANGE[0],
                max_value=WEIGHT_RANGE[1],
                value=st.session_state.user_info["weight"],
                step=1
            )
        
        # 保存步骤1数据
        st.session_state.user_info.update({
            "gender": gender,
            "age": age,
            "height": height,
            "weight": weight
        })
        
        # 按钮：下一步
        col_empty, col_next = st.columns([4, 1])
        with col_next:
            next_btn = st.button("下一步 →", type="primary", use_container_width=True)
        if next_btn:
            st.session_state.questionnaire_step = 2
            st.rerun()
        
        return st.session_state.user_info, st.session_state.user_preferences, False
    
    # 步骤2：偏好设置（修复各选项索引逻辑）
    elif current_step == 2:
        col1, col2 = st.columns(2)
        with col1:
            # 安全获取 region 索引
            region_value = st.session_state.user_preferences["region"]
            region_index = list(REGION_RATIO.keys()).index(region_value) if region_value in REGION_RATIO.keys() else 0
            region = st.selectbox(
                "希望伴侣所在地区",
                options=list(REGION_RATIO.keys()),
                index=region_index
            )
            
            # 安全获取 orientation 索引
            ori_value = st.session_state.user_preferences["orientation"]
            ori_index = list(ORIENTATION_RATIO.keys()).index(ori_value) if ori_value in ORIENTATION_RATIO.keys() else 0
            orientation = st.radio(
                "你的情感取向",
                options=list(ORIENTATION_RATIO.keys()),
                horizontal=True,
                index=ori_index
            )
            
            # 安全获取 personality 索引
            personality_value = st.session_state.user_preferences["personality"]
            personality_index = PARTNER_PERSONALITY_TYPES.index(personality_value) if personality_value in PARTNER_PERSONALITY_TYPES else 0
            personality = st.selectbox(
                "喜欢的伴侣性格",
                options=PARTNER_PERSONALITY_TYPES,
                index=personality_index
            )
        with col2:
            st.markdown("### 你的爱好（可多选）")
            hobbies = st.multiselect(
                "",
                options=USER_HOBBIES_OPTIONS,
                default=st.session_state.user_preferences["hobbies"]
            )
        
        # 保存步骤2数据
        st.session_state.user_preferences.update({
            "region": region,
            "orientation": orientation,
            "personality": personality,
            "hobbies": hobbies
        })
        
        # 按钮：上一步/完成
        col_prev, col_empty, col_finish = st.columns([1, 2, 1])
        with col_prev:
            prev_btn = st.button("← 上一步", use_container_width=True)
        with col_finish:
            finish_btn = st.button("完成并匹配", type="primary", use_container_width=True)
        
        if prev_btn:
            st.session_state.questionnaire_step = 1
            st.rerun()
        if finish_btn:
            return st.session_state.user_info, st.session_state.user_preferences, True
    
    return st.session_state.user_info, st.session_state.user_preferences, False

# ========== 其他原有组件保持不变（略去重复代码） ==========
def render_match_pool_preview(user_info: dict, user_preferences: dict):
    from config import ALIVE_HUMANS
    region = user_preferences["region"]
    pool_size = round(ALIVE_HUMANS * REGION_RATIO[region] * 0.07, 1)
    personality = user_preferences["personality"]
    hobbies = ", ".join(user_preferences["hobbies"]) if user_preferences["hobbies"] else "无明确偏好"
    
    st.markdown(f"""
    ### 👥 你的匹配池预览
    年龄{user_info['age']}岁+{region}地区+年龄相近+偏好{personality}性格+喜欢{hobbies}的潜在伴侣：**{pool_size}亿人**
    """)
    st.markdown("---")

def render_match_analysis(base_prob: float, preference_fit: float, final_prob: float, suggestion: str):
    st.markdown("---")
    st.subheader("📊 匹配分析")
    
    # 概率卡片
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="background: #e8f4f8; border-radius: 8px; padding: 15px; text-align: center;">
            <p style="margin: 0 0 8px 0; color: #4a5568; font-size: 14px;">基础匹配概率</p>
            <p style="margin: 0; color: #2d3748; font-size: 20px; font-weight: bold;">{base_prob}%</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background: #fdf2f8; border-radius: 8px; padding: 15px; text-align: center;">
            <p style="margin: 0 0 8px 0; color: #4a5568; font-size: 14px;">偏好契合度</p>
            <p style="margin: 0; color: #e53e3e; font-size: 20px; font-weight: bold;">{preference_fit}分</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background: #f5fafe; border-radius: 8px; padding: 15px; text-align: center;">
            <p style="margin: 0 0 8px 0; color: #4a5568; font-size: 14px;">最终匹配概率</p>
            <p style="margin: 0; color: #38b2ac; font-size: 20px; font-weight: bold;">{final_prob}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 匹配建议
    st.markdown(f"""
    <div style="background: #f8f8f8; border-radius: 8px; padding: 15px; margin-top: 15px;">
        <p style="margin: 0 0 8px 0; color: #2d3748; font-weight: bold;">💡 匹配建议</p>
        <p style="margin: 0; color: #4a5568; font-size: 16px;">{suggestion}</p>
    </div>
    """, unsafe_allow_html=True)

# 其他组件（render_partner_card、render_partner_personality 等）保持不变
def render_partner_card(
    partner_era: str, partner_era_label: str,
    partner_job: str, match_prob: float,
    meeting_story: str
):
    card_html = f"""
    <div style="border: 2px solid #f0f2f6; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
        <h3 style="color: #2e4057; margin: 0 0 15px 0;">💘 你的随机灵魂伴侣</h3>
        <div style="display: flex; gap: 20px; margin-bottom: 15px;">
            <div style="flex: 1; text-align: center; padding: 10px; background: #f8f9fa; border-radius: 8px;">
                <p style="margin: 0; color: #4a5568; font-size: 14px;">伴侣时代</p>
                <p style="margin: 5px 0 0 0; color: #2d3748; font-size: 18px; font-weight: bold;">{partner_era_label}</p>
            </div>
            <div style="flex: 1; text-align: center; padding: 10px; background: #f8f9fa; border-radius: 8px;">
                <p style="margin: 0; color: #4a5568; font-size: 14px;">职业</p>
                <p style="margin: 5px 0 0 0; color: #2d3748; font-size: 18px; font-weight: bold;">{partner_job}</p>
            </div>
            <div style="flex: 1; text-align: center; padding: 10px; background: #f8f9fa; border-radius: 8px;">
                <p style="margin: 0; color: #4a5568; font-size: 14px;">最终匹配概率</p>
                <p style="margin: 5px 0 0 0; color: #e53e3e; font-size: 18px; font-weight: bold;">{match_prob}%</p>
            </div>
        </div>
        <div style="background: #fef7fb; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
            <p style="margin: 0; color: #2d3748; font-size: 16px;">📖 相遇场景：{meeting_story}</p>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def render_partner_personality(personality: dict):
    st.markdown("---")
    st.subheader("👤 伴侣档案")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background: #e8f4f8; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
            <p style="margin: 0 0 8px 0; color: #2d3748; font-weight: bold;">性格</p>
            <p style="margin: 0; color: #4a5568;">{', '.join(personality['personality'])}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background: #fdf2f8; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
            <p style="margin: 0 0 8px 0; color: #2d3748; font-weight: bold;">爱好</p>
            <p style="margin: 0; color: #4a5568;">{', '.join(personality['hobbies'])}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background: #f5fafe; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
            <p style="margin: 0 0 8px 0; color: #2d3748; font-weight: bold;">口头禅</p>
            <p style="margin: 0; color: #4a5568; font-size: 16px;">"{personality['catchphrase']}"</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background: #fcf1f7; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
            <p style="margin: 0 0 8px 0; color: #2d3748; font-weight: bold;">说话风格</p>
            <p style="margin: 0; color: #4a5568;">{personality['speaking_style']}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background: #f8f8f8; border-radius: 8px; padding: 15px;">
        <p style="margin: 0 0 8px 0; color: #2d3748; font-weight: bold;">背景小故事</p>
        <p style="margin: 0; color: #4a5568;">{personality['background']}</p>
    </div>
    """, unsafe_allow_html=True)

def render_chat_history(chat_history: list):
    st.markdown("---")
    st.subheader("💬 聊天记录")
    chat_container = st.container(height=300)
    with chat_container:
        for msg in chat_history:
            role = msg["role"]
            content = msg["content"]
            time = msg["time"]
            if role == "user":
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                    <div style="background: #4299e1; color: white; padding: 8px 12px; border-radius: 12px 12px 0 12px; max-width: 70%;">
                        <p style="margin: 0; font-size: 14px;">{content}</p>
                        <p style="margin: 4px 0 0 0; font-size: 11px; opacity: 0.8;">{time}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif role == "partner":
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
                    <div style="background: #f0f2f6; color: #2d3748; padding: 8px 12px; border-radius: 12px 12px 12px 0; max-width: 70%;">
                        <p style="margin: 0; font-size: 14px;">{content}</p>
                        <p style="margin: 4px 0 0 0; font-size: 11px; opacity: 0.8;">{time}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

def render_chat_input() -> str:
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    with col1:
        user_message = st.text_input("输入你想对伴侣说的话...", placeholder="比如：你平时喜欢做什么？")
    with col2:
        send_btn = st.button("发送", type="primary", use_container_width=True)
    if send_btn and user_message.strip():
        return user_message.strip()
    return ""

def render_probability科普():
    with st.expander("📊 为什么匹配概率这么低？", expanded=False):
        labels = ["已去世人类", "现存人类", "未来人类（虚构）"]
        values = [93, 7, 0.1]
        colors = ["#9f7aea", "#4299e1", "#38b2ac"]
        fig = px.pie(values=values, names=labels, color=labels, color_discrete_map=dict(zip(labels, colors)), hole=0.5, title="人类历史人口分布")
        fig.update_layout(title_font=dict(size=14), legend_font=dict(size=12))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""
        ### 概率逻辑说明：
        1. 人类历史上约**93%的人已经去世**，现存仅7%；
        2. 现存人口中，与你年龄相近（±5岁）的仅占7%；
        3. 叠加地区、取向等条件后，匹配概率会进一步降低；
        4. 未来人类为虚构设定，仅为增加趣味～
        """)

def render_action_buttons() -> tuple:
    col1, col2 = st.columns(2)
    with col1:
        confirm_btn = st.button("👍 确认这个伴侣", type="primary", use_container_width=True)
    with col2:
        retry_btn = st.button("👎 重新匹配", use_container_width=True)
    return confirm_btn, retry_btn

def render_match_settings() -> tuple:
    # 兼容原有代码，避免报错
    return 25, "全球", "不限"