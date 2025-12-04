import streamlit as st
import plotly.express as px
from config import (
    PARTNER_ERAS, PARTNER_JOBS, REGION_RATIO, ORIENTATION_RATIO,
    QUESTIONNAIRE_STEPS, GENDER_OPTIONS, HEIGHT_RANGE, WEIGHT_RANGE,
    USER_HOBBIES_OPTIONS, PARTNER_PERSONALITY_TYPES
)

# ========== 新增：推进式问卷组件 ==========
def render_questionnaire() -> tuple[dict, dict, bool]:
    """
    渲染推进式问卷（分2步）
    :return: (玩家基本信息, 玩家偏好, 是否完成问卷)
    """
    # 初始化问卷状态
    if "questionnaire_step" not in st.session_state:
        st.session_state.questionnaire_step = 1
    if "user_info" not in st.session_state:
        st.session_state.user_info = {
            "gender": GENDER_OPTIONS[0],
            "age": 25,
            "height": 170,
            "weight": 60
        }
    if "user_preferences" not in st.session_state:
        st.session_state.user_preferences = {
            "region": "全球",
            "orientation": "不限",
            "personality": PARTNER_PERSONALITY_TYPES[0],
            "hobbies": []
        }
    
    current_step = st.session_state.questionnaire_step
    step_config = QUESTIONNAIRE_STEPS[current_step - 1]
    
    # 问卷标题与进度
    st.markdown(f"""
    ### 📝 {step_config['step']}/{len(QUESTIONNAIRE_STEPS)} {step_config['title']}
    <p style="color: #666; margin-bottom: 20px;">{step_config['desc']}</p>
    """, unsafe_allow_html=True)
    
    # 步骤1：基本信息
    if current_step == 1:
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox(
                "你的性别",
                options=GENDER_OPTIONS,
                index=GENDER_OPTIONS.index(st.session_state.user_info["gender"])
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
    
    # 步骤2：偏好设置
    elif current_step == 2:
        col1, col2 = st.columns(2)
        with col1:
            region = st.selectbox(
                "希望伴侣所在地区",
                options=list(REGION_RATIO.keys()),
                index=list(REGION_RATIO.keys()).index(st.session_state.user_preferences["region"])
            )
            orientation = st.radio(
                "你的情感取向",
                options=list(ORIENTATION_RATIO.keys()),
                horizontal=True,
                index=list(ORIENTATION_RATIO.keys()).index(st.session_state.user_preferences["orientation"])
            )
            personality = st.selectbox(
                "喜欢的伴侣性格",
                options=PARTNER_PERSONALITY_TYPES,
                index=PARTNER_PERSONALITY_TYPES.index(st.session_state.user_preferences["personality"])
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

# ========== 原有组件优化：匹配池预览（结合问卷数据） ==========
def render_match_pool_preview(user_info: dict, user_preferences: dict):
    """渲染匹配池预览（显示偏好相关信息）"""
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

# ========== 新增：匹配概率与建议展示组件 ==========
def render_match_analysis(base_prob: float, preference_fit: float, final_prob: float, suggestion: str):
    """展示匹配概率分析和建议"""
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

# ========== 原有组件保持不变（略去重复代码，仅保留新增/修改部分） ==========
def render_match_settings() -> tuple:
    # 该函数已被推进式问卷替代，保留但不再使用（避免报错）
    pass

def render_partner_card(
    partner_era: str, partner_era_label: str,
    partner_job: str, match_prob: float,
    meeting_story: str
):
    # 原有逻辑不变，略
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

# 其他原有组件（render_partner_personality、render_chat_history、render_chat_input等）保持不变，略
def render_partner_personality(personality: dict):
    # 原有逻辑不变，略
    pass

def render_chat_history(chat_history: list):
    # 原有逻辑不变，略
    pass

def render_chat_input() -> str:
    # 原有逻辑不变，略
    pass

def render_probability科普():
    # 原有逻辑不变，略
    pass

def render_action_buttons() -> tuple:
    # 原有逻辑不变，略
    pass