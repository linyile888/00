import streamlit as st
import random
from config import PARTNER_ERAS, PARTNER_JOBS
from utils import calculate_match_probability, generate_meeting_story, get_reject_text
from ui_components import (
    render_match_settings, render_match_pool_preview,
    render_partner_card, render_probability科普,
    render_action_buttons
)

# ========== 页面基础设置 ==========
st.set_page_config(
    page_title="随机灵魂伴侣匹配器",
    page_icon="💘",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("💘 随机灵魂伴侣匹配器")
st.markdown("穿越时空，匹配你的专属灵魂伴侣～ 概率低到离谱！")

# ========== 初始化Session状态（保存匹配历史/当前结果） ==========
if "current_match" not in st.session_state:
    st.session_state.current_match = None  # 存储当前匹配结果
if "match_history" not in st.session_state:
    st.session_state.match_history = []  # 存储匹配历史

# ========== 核心流程 ==========
def main():
    # 1. 渲染侧边栏设置，获取用户输入
    age, region, orientation = render_match_settings()
    
    # 2. 渲染匹配池预览
    render_match_pool_preview(age, region)
    
    # 3. 匹配按钮（主页面核心交互）
    col_center = st.columns(3)[1]  # 居中显示按钮
    with col_center:
        match_btn = st.button("🎲 开启随机伴侣匹配", type="primary", use_container_width=True)
    
    # 4. 执行匹配逻辑
    if match_btn or st.session_state.current_match:
        # 随机选择伴侣时代和职业
        selected_era, selected_era_label = random.choice(PARTNER_ERAS)
        selected_job = random.choice(PARTNER_JOBS[selected_era])
        
        # 计算匹配概率
        match_prob = calculate_match_probability(age, region, orientation)
        
        # 生成相遇场景
        meeting_story = generate_meeting_story(age, region, selected_era, selected_job)
        
        # 保存当前匹配结果到Session
        st.session_state.current_match = {
            "era": selected_era,
            "era_label": selected_era_label,
            "job": selected_job,
            "prob": match_prob,
            "story": meeting_story
        }
        
        # 5. 渲染伴侣卡片
        render_partner_card(
            partner_era=selected_era,
            partner_era_label=selected_era_label,
            partner_job=selected_job,
            match_prob=match_prob,
            meeting_story=meeting_story
        )
        
        # 6. 渲染操作按钮
        confirm_btn, retry_btn = render_action_buttons()
        
        # 7. 处理按钮交互
        if confirm_btn:
            # 保存到历史记录
            st.session_state.match_history.append(st.session_state.current_match)
            st.success("🎉 恭喜！已锁定你的灵魂伴侣～")
        
        if retry_btn:
            # 显示吐槽文案，刷新页面
            st.info(get_reject_text())
            st.session_state.current_match = None  # 清空当前结果，触发重新匹配
            st.rerun()  # 刷新页面
    
    # 8. 渲染概率科普区（折叠面板）
    render_probability科普()

if __name__ == "__main__":
    main()