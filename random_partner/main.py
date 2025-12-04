import streamlit as st
import random
from datetime import datetime
from config import PARTNER_ERAS, PARTNER_JOBS
from utils import (
    calculate_match_probability, generate_meeting_story, get_reject_text,
    generate_partner_personality, save_chat_history, generate_partner_reply  # 新增导入
)
from ui_components import (
    render_match_settings, render_match_pool_preview,
    render_partner_card, render_probability科普,
    render_action_buttons,
    render_partner_personality, render_chat_history, render_chat_input  # 新增导入
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

# ========== 初始化Session状态（新增交流相关状态） ==========
if "current_match" not in st.session_state:
    st.session_state.current_match = None  # 存储当前匹配结果（含人物设定）
if "match_history" not in st.session_state:
    st.session_state.match_history = []  # 存储匹配历史
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # 存储当前聊天记录
if "is_chatting" not in st.session_state:
    st.session_state.is_chatting = False  # 是否进入交流模式

# ========== 核心流程 ==========
def main():
    # 1. 渲染侧边栏设置，获取用户输入
    age, region, orientation = render_match_settings()
    
    # 2. 渲染匹配池预览
    render_match_pool_preview(age, region)
    
    # 3. 匹配按钮（主页面核心交互）
    col_center = st.columns(3)[1]
    with col_center:
        match_btn = st.button("🎲 开启随机伴侣匹配", type="primary", use_container_width=True)
    
    # 4. 执行匹配逻辑（生成伴侣信息+人物设定）
    if match_btn or st.session_state.current_match:
        # 若点击匹配按钮，重新生成伴侣信息
        if match_btn:
            selected_era, selected_era_label = random.choice(PARTNER_ERAS)
            selected_job = random.choice(PARTNER_JOBS[selected_era])
            match_prob = calculate_match_probability(age, region, orientation)
            meeting_story = generate_meeting_story(age, region, selected_era, selected_job)
            # 新增：生成伴侣人物设定
            partner_personality = generate_partner_personality(selected_era, selected_job)
            
            # 保存当前匹配结果（含人物设定）
            st.session_state.current_match = {
                "era": selected_era,
                "era_label": selected_era_label,
                "job": selected_job,
                "prob": match_prob,
                "story": meeting_story,
                "personality": partner_personality,
                "user_info": {"age": age, "region": region}  # 存储用户信息，用于交流
            }
            # 重置聊天记录
            st.session_state.chat_history = []
            st.session_state.is_chatting = False
        
        # 获取当前匹配结果
        current_match = st.session_state.current_match
        if not current_match:
            return
        
        # 5. 渲染伴侣卡片
        render_partner_card(
            partner_era=current_match["era"],
            partner_era_label=current_match["era_label"],
            partner_job=current_match["job"],
            match_prob=current_match["prob"],
            meeting_story=current_match["story"]
        )
        
        # 6. 渲染操作按钮（确认/重新匹配）
        confirm_btn, retry_btn = render_action_buttons()
        
        # 7. 处理按钮交互
        if retry_btn:
            st.info(get_reject_text())
            st.session_state.current_match = None
            st.session_state.chat_history = []
            st.session_state.is_chatting = False
            st.rerun()
        
        # 8. 确认伴侣后，进入交流模式
        if confirm_btn:
            st.session_state.is_chatting = True
            # 保存到匹配历史
            if current_match not in st.session_state.match_history:
                st.session_state.match_history.append(current_match)
            st.success("🎉 已确认伴侣！现在可以和TA交流啦～")
        
        # 9. 交流模式：展示人物设定、聊天记录、输入框
        if st.session_state.is_chatting:
            # 渲染伴侣人物设定
            render_partner_personality(current_match["personality"])
            
            # 渲染聊天记录
            render_chat_history(st.session_state.chat_history)
            
            # 渲染聊天输入框，获取用户消息
            user_message = render_chat_input()
            if user_message:
                # 记录用户消息（带时间戳）
                user_msg_item = {
                    "role": "user",
                    "content": user_message,
                    "time": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.chat_history.append(user_msg_item)
                
                # 生成伴侣回复
                partner_reply = generate_partner_reply(
                    user_age=current_match["user_info"]["age"],
                    user_region=current_match["user_info"]["region"],
                    partner_info=current_match,
                    user_message=user_message
                )
                
                # 记录伴侣消息（带时间戳）
                partner_msg_item = {
                    "role": "partner",
                    "content": partner_reply,
                    "time": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.chat_history.append(partner_msg_item)
                
                # 自动保存聊天记录（每次交流后保存）
                save_path = save_chat_history(
                    partner_info={
                        "era": current_match["era"],
                        "job": current_match["job"],
                        "personality": current_match["personality"]
                    },
                    chat_history=st.session_state.chat_history
                )
                # 提示保存成功（短暂显示）
                st.success(f"💾 聊天记录已保存至：{save_path}", icon="💾")
                
                # 刷新页面，显示最新聊天记录
                st.rerun()
        
        # 10. 渲染概率科普区
        render_probability科普()

if __name__ == "__main__":
    main()