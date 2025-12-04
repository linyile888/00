import streamlit as st
import plotly.express as px
from config import (
    PARTNER_ERAS, PARTNER_JOBS,
    REGION_RATIO, ORIENTATION_RATIO  # 已导入，无需修改
)

# ========== 原有函数保持不变 ==========
def render_match_settings() -> tuple:
    st.sidebar.header("🎯 匹配设置")
    age = st.sidebar.slider("你的年龄", min_value=18, max_value=60, value=25, step=1)
    region = st.sidebar.selectbox("希望伴侣所在地区", options=list(REGION_RATIO.keys()), index=0)
    orientation = st.sidebar.radio("你的情感取向", options=list(ORIENTATION_RATIO.keys()), horizontal=True)
    st.sidebar.markdown("---")
    st.sidebar.info("设置完成后，点击主页面「开启匹配」按钮～")
    return age, region, orientation

def render_match_pool_preview(age: int, region: str):
    from config import ALIVE_HUMANS
    pool_size = round(ALIVE_HUMANS * REGION_RATIO[region] * 0.07, 1)
    st.markdown(f"""
    ### 👥 你的匹配池预览
    年龄{age}岁+{region}地区+年龄相近的潜在伴侣：**{pool_size}亿人**
    """)
    st.markdown("---")

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
                <p style="margin: 0; color: #4a5568; font-size: 14px;">伴侣时代</p >
                <p style="margin: 5px 0 0 0; color: #2d3748; font-size: 18px; font-weight: bold;">{partner_era_label}</p >
            </div>
            <div style="flex: 1; text-align: center; padding: 10px; background: #f8f9fa; border-radius: 8px;">
                <p style="margin: 0; color: #4a5568; font-size: 14px;">职业</p >
                <p style="margin: 5px 0 0 0; color: #2d3748; font-size: 18px; font-weight: bold;">{partner_job}</p >
            </div>
            <div style="flex: 1; text-align: center; padding: 10px; background: #f8f9fa; border-radius: 8px;">
                <p style="margin: 0; color: #4a5568; font-size: 14px;">匹配概率</p >
                <p style="margin: 5px 0 0 0; color: #e53e3e; font-size: 18px; font-weight: bold;">{match_prob}%</p >
            </div>
        </div>
        <div style="background: #fef7fb; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
            <p style="margin: 0; color: #2d3748; font-size: 16px;">📖 相遇场景：{meeting_story}</p >
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

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

# ========== 新增：人物设定展示组件 ==========
def render_partner_personality(personality: dict):
    """展示伴侣详细人物设定"""
    st.markdown("---")
    st.subheader("👤 伴侣档案")
    # 用卡片样式展示各项设定
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background: #e8f4f8; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
            <p style="margin: 0 0 8px 0; color: #2d3748; font-weight: bold;">性格</p >
            <p style="margin: 0; color: #4a5568;">{', '.join(personality['personality'])}</p >
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background: #fdf2f8; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
            <p style="margin: 0 0 8px 0; color: #2d3748; font-weight: bold;">爱好</p >
            <p style="margin: 0; color: #4a5568;">{', '.join(personality['hobbies'])}</p >
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background: #f5fafe; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
            <p style="margin: 0 0 8px 0; color: #2d3748; font-weight: bold;">口头禅</p >
            <p style="margin: 0; color: #4a5568; font-size: 16px;">"{personality['catchphrase']}"</p >
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background: #fcf1f7; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
            <p style="margin: 0 0 8px 0; color: #2d3748; font-weight: bold;">说话风格</p >
            <p style="margin: 0; color: #4a5568;">{personality['speaking_style']}</p >
        </div>
        """, unsafe_allow_html=True)
    # 背景小故事
    st.markdown(f"""
    <div style="background: #f8f8f8; border-radius: 8px; padding: 15px;">
        <p style="margin: 0 0 8px 0; color: #2d3748; font-weight: bold;">背景小故事</p >
        <p style="margin: 0; color: #4a5568;">{personality['background']}</p >
    </div>
    """, unsafe_allow_html=True)

# ========== 新增：聊天记录展示组件 ==========
def render_chat_history(chat_history: list):
    """展示历史聊天记录"""
    st.markdown("---")
    st.subheader("💬 聊天记录")
    # 聊天容器（固定高度，滚动显示）
    chat_container = st.container(height=300)
    with chat_container:
        for msg in chat_history:
            role = msg["role"]
            content = msg["content"]
            time = msg["time"]
            # 用户消息（右对齐）
            if role == "user":
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                    <div style="background: #4299e1; color: white; padding: 8px 12px; border-radius: 12px 12px 0 12px; max-width: 70%;">
                        <p style="margin: 0; font-size: 14px;">{content}</p >
                        <p style="margin: 4px 0 0 0; font-size: 11px; opacity: 0.8;">{time}</p >
                    </div>
                </div>
                """, unsafe_allow_html=True)
            # 伴侣消息（左对齐）
            elif role == "partner":
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
                    <div style="background: #f0f2f6; color: #2d3748; padding: 8px 12px; border-radius: 12px 12px 12px 0; max-width: 70%;">
                        <p style="margin: 0; font-size: 14px;">{content}</p >
                        <p style="margin: 4px 0 0 0; font-size: 11px; opacity: 0.8;">{time}</p >
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ========== 新增：交流输入框组件 ==========
def render_chat_input() -> str:
    """渲染聊天输入框"""
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    with col1:
        user_message = st.text_input("输入你想对伴侣说的话...", placeholder="比如：你平时喜欢做什么？")
    with col2:
        send_btn = st.button("发送", type="primary", use_container_width=True)
    # 按回车或点击发送按钮返回消息
    if send_btn and user_message.strip():
        return user_message.strip()
    return ""