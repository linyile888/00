import streamlit as st
import plotly.express as px
from config import (
    PARTNER_ERAS, PARTNER_JOBS,
    REGION_RATIO, ORIENTATION_RATIO  # 新增：导入缺失的配置变量
)

def render_match_settings() -> tuple:
    """
    渲染匹配设置（侧边栏）
    :return: (age, region, orientation) - 用户选择的参数
    """
    st.sidebar.header("🎯 匹配设置")
    
    # 年龄滑块
    age = st.sidebar.slider(
        "你的年龄",
        min_value=18,
        max_value=60,
        value=25,
        step=1
    )
    
    # 地区下拉框（使用导入的 REGION_RATIO）
    region = st.sidebar.selectbox(
        "希望伴侣所在地区",
        options=list(REGION_RATIO.keys()),
        index=0
    )
    
    # 取向单选框（使用导入的 ORIENTATION_RATIO）
    orientation = st.sidebar.radio(
        "你的情感取向",
        options=list(ORIENTATION_RATIO.keys()),
        horizontal=True
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("设置完成后，点击主页面「开启匹配」按钮～")
    
    return age, region, orientation

def render_match_pool_preview(age: int, region: str):
    """渲染匹配池预览（主页面顶部）"""
    from config import ALIVE_HUMANS  # 局部导入，避免循环导入
    # 计算匹配池人数（亿）
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
    """
    渲染伴侣结果卡片（核心UI）
    :param partner_era: 伴侣时代（纯文本）
    :param partner_era_label: 伴侣时代（带图标）
    :param partner_job: 伴侣职业
    :param match_prob: 匹配概率
    :param meeting_story: 相遇场景
    """
    # 卡片样式（用markdown实现整洁边框）
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
    """渲染概率科普区（折叠面板）"""
    with st.expander("📊 为什么匹配概率这么低？", expanded=False):
        # 生成环形图（时代分布概率）
        labels = ["已去世人类", "现存人类", "未来人类（虚构）"]
        values = [93, 7, 0.1]
        colors = ["#9f7aea", "#4299e1", "#38b2ac"]
        
        fig = px.pie(
            values=values,
            names=labels,
            color=labels,
            color_discrete_map=dict(zip(labels, colors)),
            hole=0.5,
            title="人类历史人口分布"
        )
        fig.update_layout(title_font=dict(size=14), legend_font=dict(size=12))
        st.plotly_chart(fig, use_container_width=True)
        
        # 科普文字
        st.markdown("""
        ### 概率逻辑说明：
        1. 人类历史上约**93%的人已经去世**，现存仅7%；
        2. 现存人口中，与你年龄相近（±5岁）的仅占7%；
        3. 叠加地区、取向等条件后，匹配概率会进一步降低；
        4. 未来人类为虚构设定，仅为增加趣味～
        """)

def render_action_buttons() -> tuple:
    """渲染操作按钮（确认/重新匹配）"""
    col1, col2 = st.columns(2)
    with col1:
        confirm_btn = st.button("👍 确认这个伴侣", type="primary", use_container_width=True)
    with col2:
        retry_btn = st.button("👎 重新匹配", use_container_width=True)
    return confirm_btn, retry_btn